"""Transport/immutability fixtures; real publication replay is tested on delivery."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import export_reviewed_handoff as h


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.stage=self.root/'stage';self.stage.mkdir();source=self.stage/'source';source.mkdir()
        def put(name,text):
            p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        put('data/moratorium_inventory.csv','moratorium_id\nlocal-1\nlocal-2\n')
        put('data/state_legislation.csv','policy_action_id\nstate-1\n')
        put('data/summary_stats.json','{}')
        for name,n in [('ballot_measures',1),('measure_results',2),('instrument_events',1),('local_restrictions',1),('measure_instrument_links',1)]:
            put('data/expanded-snapshots/generation/'+name+'.jsonl',''.join(json.dumps({'fixture_id':i})+'\n' for i in range(n)))
        put('data/expanded-snapshots/generation/publication.json',json.dumps({'sha256':'a'*64,'plan':{'reviewed_at':'2026-11-06T12:00:00Z','validation_profile':{'name':'1.0.2'}}}))
        put('data/expanded-csv-snapshots/projection/measure_results_current.csv','result_id\nresult-1\n')
        put('data/expanded-csv-snapshots/projection/instrument_events_current.csv','event_id\nevent-1\n')
        put('data/expanded-csv-snapshots/projection/instrument_event_status.csv','event_id,review_state\nevent-1,accepted\n')
        put('data/expanded-csv-snapshots/projection/manifest.json',json.dumps({'files':{'measure_results_current.csv':{},'instrument_events_current.csv':{}}}))
        (source/'data/expanded').symlink_to('expanded-snapshots/generation')
        (source/'data/expanded-csv').symlink_to('expanded-csv-snapshots/projection')
        upstream={'source_commit':'f'*40,'files':h.inventory(source,source_tree=True)}
        (self.stage/'upstream-manifest.json').write_bytes(h.encode(upstream))
        aliases=h.alias_specs(source)
        for alias in aliases:
            target=self.stage/alias['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((self.stage/alias['source_path']).read_bytes())
        (self.stage/'verify_handoff.py').write_text('Synthetic verifier placeholder; never executed.\n')
        self.manifest={'exporter_source_commit':'f'*40,'source_exporter_sha256':h.sha((self.stage/'verify_handoff.py').read_bytes()),'schema_version':h.VERSION,'source_commit':'f'*40,'upstream_manifest_sha256':h.sha((self.stage/'upstream-manifest.json').read_bytes()),
                       'files':h.inventory(self.stage),'compatibility_aliases':aliases,**h.current_metadata(source)}
        self.seal()

    def seal(self):
        (self.stage/'manifest.json').write_bytes(h.encode(self.manifest));self.pin=h.sha((self.stage/'manifest.json').read_bytes())

    def test_source_order_handles_base_and_patch_release_directories(self):
        root=self.root/'ordering';root.mkdir()
        names=['release-2026.11.9/README.md','release-2026.11.9.post1/README.md']
        for name in names:
            path=root/name;path.parent.mkdir();path.write_text(name)
        self.assertEqual([r['path'] for r in h.inventory(root,source_tree=True)],sorted(names))
        # Existing handoff manifests include directories in Path component order.
        self.assertEqual([r['path'] for r in h.inventory(root) if r['kind']=='file'],names)

    def test_counts_are_separate_and_profile2_event_acceptance_is_explicit(self):
        result=h.verify_handoff(self.stage,self.pin,run_checks=False)
        self.assertEqual(result['state'],'verified');self.assertFalse(result['checks_run'])
        self.assertEqual(self.manifest['current_counts']['moratorium_records'],2)
        self.assertEqual(self.manifest['current_counts']['ballot_measures'],1)
        self.assertEqual(self.manifest['current_counts']['retained_results'],2)
        self.assertEqual(self.manifest['current_counts']['current_results'],1)
        self.assertEqual(self.manifest['current_counts']['current_accepted_historical_events'],1)

    def test_wrong_external_pin_prevents_packaged_code_execution(self):
        with patch.object(h,'run_source_checks') as checks:
            with self.assertRaisesRegex(ValueError,'manifest fingerprint'):h.verify_handoff(self.stage,'0'*64)
            checks.assert_not_called()

    def test_mixed_compatibility_bytes_or_incomplete_alias_set_fail(self):
        (self.stage/'expanded/ballot_measures.jsonl').write_text('{}\n')
        with self.assertRaisesRegex(ValueError,'file set'):h.verify_handoff(self.stage,self.pin,run_checks=False)
        self.manifest['files']=h.inventory(self.stage);self.seal()
        with self.assertRaisesRegex(ValueError,'alias differs'):h.verify_handoff(self.stage,self.pin,run_checks=False)

    def test_count_or_profile_metadata_cannot_disagree_with_source(self):
        self.manifest['current_counts']['ballot_measures']=True;self.seal()
        with self.assertRaisesRegex(ValueError,'metadata/profile/counts'):h.verify_handoff(self.stage,self.pin,run_checks=False)

    def test_source_manifest_coverage_cannot_drop_history_file(self):
        upstream=json.loads((self.stage/'upstream-manifest.json').read_text());upstream['files'].pop()
        (self.stage/'upstream-manifest.json').write_bytes(h.encode(upstream));self.manifest['upstream_manifest_sha256']=h.sha((self.stage/'upstream-manifest.json').read_bytes());self.manifest['files']=h.inventory(self.stage);self.seal()
        with self.assertRaisesRegex(ValueError,'Source replay tree'):h.verify_handoff(self.stage,self.pin,run_checks=False)

    def test_traversal_unknown_files_and_escaping_symlinks_are_rejected(self):
        self.manifest['files'][0]['path']='../outside';self.seal()
        with self.assertRaisesRegex(ValueError,'Unsafe handoff path'):h.verify_handoff(self.stage,self.pin,run_checks=False)
        (self.stage/'escape').symlink_to(self.root)
        with self.assertRaisesRegex(ValueError,'Unexpected handoff symlink|symlink escapes'):h.inventory(self.stage)

    def test_atomic_create_exact_replay_and_different_bytes_refusal(self):
        destination=self.root/'delivery'
        self.assertEqual(h.publish_tree(self.stage,destination),'created')
        second=self.root/'second';shutil.copytree(destination,second,symlinks=True)
        self.assertEqual(h.publish_tree(second,destination),'already_present')
        (destination/'expanded/ballot_measures.jsonl').write_text('different')
        with self.assertRaisesRegex(ValueError,'file set'):h.publish_tree(second,destination)
        self.assertEqual((destination/'expanded/ballot_measures.jsonl').read_text(),'different')

    def test_reader_cannot_modify_source_tree_during_checks(self):
        def change(root):
            (root/'source/unexpected').write_text('changed');return []
        with patch.object(h,'run_source_checks',side_effect=change):
            with self.assertRaisesRegex(ValueError,'file set'):h.verify_handoff(self.stage,self.pin)

    def test_extra_empty_directory_and_contained_unexpected_symlink_fail(self):
        (self.stage/'unexpected').mkdir()
        with self.assertRaisesRegex(ValueError,'file set'):h.verify_handoff(self.stage,self.pin,run_checks=False)
        (self.stage/'unexpected').rmdir();(self.stage/'unexpected').symlink_to('expanded')
        with self.assertRaisesRegex(ValueError,'Unexpected handoff symlink'):h.inventory(self.stage)

    def test_competing_empty_destination_cannot_be_overwritten(self):
        destination=self.root/'competing';operation=h.rename_noreplace
        def compete(stage,target):
            target.mkdir();operation(stage,target)
        with patch.object(h,'rename_noreplace',side_effect=compete):
            with self.assertRaisesRegex(ValueError,'Refusing to replace existing directory'):h.publish_tree(self.stage,destination)
        self.assertTrue(destination.is_dir());self.assertEqual(list(destination.iterdir()),[])
        self.assertTrue((self.stage/'manifest.json').is_file())

    def test_uncommitted_exporter_cannot_label_worktree_bytes_with_head(self):
        destination=self.root/'uncreated-parent/output'
        with patch.object(h.subprocess,'check_output',side_effect=['f'*40+'\n',b'different committed exporter']):
            with self.assertRaisesRegex(ValueError,'Commit the exact exporter'):h.export(destination)
        self.assertFalse(destination.parent.exists())

    def test_changed_bundle_builder_is_rejected_before_output_creation(self):
        destination=self.root/'uncreated-parent/output'
        with patch.object(h.subprocess,'check_output',side_effect=['f'*40+'\n',Path(h.__file__).read_bytes(),b'different committed builder']):
            with self.assertRaisesRegex(ValueError,'Bundle builder differs'):h.export(destination)
        self.assertFalse(destination.parent.exists())

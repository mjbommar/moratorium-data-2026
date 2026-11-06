"""Source-supported sponsor corrections retain whole-row baseline protection."""
import contextlib
import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import apply_legislation as module


class PolicySponsorTests(unittest.TestCase):
    def exercise(self,stale):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=root/'data';data.mkdir();audit=root/'work/audit';audit.mkdir(parents=True)
            columns=module.BASE_COLUMNS+module.NEW_COLUMNS
            row={c:'' for c in columns};row.update(state='Synthetic',state_abbrev='ZZ',bill='S1',sponsors='Earlier attribution',policy_action_id='zz-s1',legal_effect_status='unknown')
            path=data/'state_legislation.csv'
            with path.open('w',newline='') as out:
                writer=csv.DictWriter(out,fieldnames=columns);writer.writeheader();writer.writerow(row)
            baseline=dict(row)
            if stale:baseline['legal_effect_status']='in_force'
            base=root/'baseline.json';base.write_text(json.dumps([baseline]))
            answers=root/'answers.json';answers.write_text(json.dumps({'state_abbrev':'ZZ','researched_as_of':'2026-11-06','researcher':'Synthetic fixture','decisions':[{'bill_key':'ZZ:S1','outcome':'corrected','fields':{'sponsors':'Reviewed primary sponsors'},'evidence':[{'url':'https://example.invalid/bill','source_type':'legislature_bill_page','supports':'Synthetic sponsor list only'}]}],'new_bills':[]}))
            with patch.object(module,'REPO',root),patch.object(module,'LEG',path),patch.object(module,'AUDIT_DIR',audit),patch.object(sys,'argv',['apply_legislation.py','--answers',str(answers),'--baseline',str(base)]),contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.main(),1 if stale else 0)
            with path.open(newline='') as stream:after=list(csv.DictReader(stream))[0]
            self.assertEqual(after['legal_effect_status'],'unknown')
            self.assertEqual(after['policy_action_id'],'zz-s1')
            if stale:
                self.assertEqual(after,row);self.assertFalse(list(audit.glob('apply-legislation-*.json')))
            else:
                receipt=json.loads(next(audit.glob('apply-legislation-*.json')).read_text())
                self.assertEqual(after,{**row,'sponsors':'Reviewed primary sponsors'})
                self.assertEqual([r['column'] for r in receipt['changes']],['sponsors'])
                self.assertFalse(receipt['conflicts'])
    def test_primary_sponsor_field_updates_without_other_changes(self):self.exercise(False)
    def test_stale_whole_row_blocks_sponsor_correction(self):self.exercise(True)


if __name__=='__main__':unittest.main()

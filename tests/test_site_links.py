"""Generated pages must not advertise nonexistent research HTML outputs."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('site_builder', Path(__file__).resolve().parents[1] / 'scripts/build_site.py')
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


class SiteLinkTests(unittest.TestCase):
    def test_generated_pages_resolve_relative_to_source(self):
        original = '<a href="../states/ohio.md#history">state</a><a href="FAQ.md?print=1#ballots">FAQ</a>'
        expected = '<a href="../states/ohio.html#history">state</a><a href="FAQ.html?print=1#ballots">FAQ</a>'
        self.assertEqual(site.rewrite_md_links(original, 'docs/codebook.md'), expected)

    def test_only_generated_readmes_become_indexes(self):
        original = '<a href="../states/README.md">states</a><a href="../work/research/case/README.md">evidence</a>'
        expected = '<a href="../states/index.html">states</a><a href="../work/research/case/README.md">evidence</a>'
        self.assertEqual(site.rewrite_md_links(original, 'docs/known-gaps.md'), expected)

    def test_unrendered_sibling_does_not_inherit_other_directory_mapping(self):
        original = '<a href="README.md">research</a><a href="../TODO.md#checks">tasks</a>'
        self.assertEqual(site.rewrite_md_links(original, 'docs/known-gaps.md'), original)

    def test_repository_readme_uses_separately_generated_landing_page(self):
        self.assertEqual(site.rewrite_md_links('<a href="../README.md#data">home</a>', 'docs/FAQ.md'), '<a href="../index.html#data">home</a>')

    def test_external_anchor_and_absolute_urls_are_preserved(self):
        original = '<a href="https://example.org/FAQ.md">remote</a><a href="//example.org/README.md">remote</a><a href="#faq">anchor</a><a href="/docs/FAQ.md">absolute</a>'
        self.assertEqual(site.rewrite_md_links(original, 'docs/codebook.md'), original)

    def test_encoded_relative_path_uses_known_output(self):
        self.assertEqual(site.rewrite_md_links('<a href="%46AQ.md#question">FAQ</a>', 'docs/codebook.md'), '<a href="FAQ.html#question">FAQ</a>')


if __name__ == '__main__':
    unittest.main()

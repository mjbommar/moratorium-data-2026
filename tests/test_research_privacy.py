"""Unclassified worker conversion output stays private even without a .private name."""
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]


class ResearchPrivacy(unittest.TestCase):
    def ignored(self,path):
        result=subprocess.run(['git','check-ignore','--no-index','-q',path],cwd=ROOT)
        self.assertIn(result.returncode,(0,1))
        return result.returncode==0

    def test_raw_conversion_aliases_are_ignored(self):
        for name in ['ordinary.txt','source.pdf','rendered.png','source.html','payload.body','payload.bin','source.private-1.png']:
            with self.subTest(name=name):
                self.assertTrue(self.ignored('work/research/test-lane/'+name))

    def test_reviewed_metadata_and_report_are_visible(self):
        for name in ['report.md','source_documents.jsonl']:
            with self.subTest(name=name):
                self.assertFalse(self.ignored('work/research/test-lane/'+name))


if __name__=='__main__':unittest.main()

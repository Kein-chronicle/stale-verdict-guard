import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RegressionTests(unittest.TestCase):
 def test_stamp_does_not_skip_linked_directories(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);src=p/'src';src.mkdir();external=p/'external';external.mkdir();(external/'x').write_text('one');(src/'x').write_text('one');(src/'linked').symlink_to(external,target_is_directory=True)
   verdict=p/'verdict.json';verdict.write_text('{}')
   r=subprocess.run([sys.executable,str(ROOT/'scripts/stamp.py'),'stamp',str(verdict),'--root',str(src)],capture_output=True)
   self.assertEqual(r.returncode,2)
if __name__=='__main__':unittest.main()

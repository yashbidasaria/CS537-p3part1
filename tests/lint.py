import toolspath
from testing import Test
import shutil
import os
import glob
# test case for lint

class LintTest(Test):
   name = "linttest"
   description = "Lint test for C programming style"   
   point_value = 6
   timeout = 5

   def run(self):
      lint_path = self.test_path + "/../../lint/"
      config_file = "CPPLINT.cfg"
      shutil.copy(lint_path + config_file, self.project_path + "/" + config_file)
      cpplint = self.test_path + "/../../lint/cpplint.py"
      
      files = glob.glob("*.c")
      self.runexe([cpplint] + ["--extensions", "c"] + files, status = 0)
      os.remove(self.project_path + "/" + config_file)
      self.done()

test_list = [LintTest]

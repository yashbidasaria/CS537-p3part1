import os, inspect

import toolspath
from testing import BuildTest
import subprocess

#curdir = os.path.dirname(inspect.getfile(inspect.currentframe()))

class StatsBuild(BuildTest):
  targets = ["all"]

  def run(self):
    self.clean(["*.o"] + ["*.so"], required=False)
    self.make(self.targets, required=False)
    self.done()

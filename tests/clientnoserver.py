import toolspath
from testing import Test
import random
import subprocess
import statsbuild
import servertest
import time
import os

class ClientNoServerTest(servertest.ServerTest):
    name = 'clientnoservertest'
    description = 'Client should exit gracefully if no server is running'
    point_value = 6
    timeout = 5

    def run(self):
        if 'LD_LIBRARY_PATH' in os.environ.keys():
            os.environ['LD_LIBRARY_PATH'] = self.project_path + ':' + os.environ['LD_LIBRARY_PATH']
        else:
            os.environ['LD_LIBRARY_PATH'] = self.project_path
        k = self.findkey()
        pid = self.runclient(k=k, p=1, c=100, s=100)
        cpid, status = os.waitpid(pid, 0)
        if os.WCOREDUMP(status):
            self.fail("You shouldn't segfault!")
        self.done()

test_list = [ClientNoServerTest]

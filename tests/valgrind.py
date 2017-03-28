import toolspath
from testing import Test
import servertest
import os
import random
import shutil
import signal
import time
import xml.etree.ElementTree

class ValgrindTest(servertest.ServerTest):
    name = 'valgrind'
    description = "essentially, manyclients2 run for longer and with valgrind"
    point_value = 6
    timeout = 65 

    def run(self):
        base_cmd = ['/usr/bin/valgrind', '--show-reachable=yes', '--xml=yes']
        vgnames = [self.project_path + '/' + str(i) + '.xml' for i in range(18)]
        key = self.findkey()
        clients = {}
        servers = {}
        s1_out = self.project_path + '/serveroutput.txt'
        cmd = base_cmd + ['--xml-file=' + vgnames[-1]]
        s1 = self.runserver(k=key, outname=s1_out, cmd=cmd)
        servers[s1] = {'pid': s1, 'key': key, 'out': s1_out}

        # Randomly pick one client to leave early
        early = random.randint(0, 15)
        time.sleep(1)

        p = 1
        for i in range(16):
            c = random.randint(3, 8)*10**8
            s = 10**9 - c
            cmd = base_cmd + ['--xml-file=' + vgnames[i]]
            c1 = self.runclient(k=key, p=p, c=c, s=s, cmd=cmd)
            clients[c1] ={'pid': c1, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}
            if i == early:
                early_pid = c1

        time.sleep(10)

        os.kill(early_pid, signal.SIGINT)
        time.sleep(1)

        # Make sure 17th client can run
        c = random.randint(3, 8)*10**8
        s = 10**9 - c
        cmd = base_cmd + ['--xml-file=' + vgnames[-2]]
        c17 = self.runclient(k=key, p=p, c=c, s=s, cmd=cmd)
        clients[c17] = {'pid': c17, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}

        time.sleep(40)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(s1_out, clients.keys())

        # Going to allow a bit of wiggle room on values since there's 17 procs
        self.check_rates(data=data, clients=clients, cnt_err=45, start=1)
        for fname in vgnames:
            summary = xml.etree.ElementTree.parse(fname).getroot()
            if summary.find('error') is not None:
                shutil.copy2(fname, 'vg_summary.xml')
                self.fail('Valgrind error, check error section of summary')
        self.done()

test_list = [ValgrindTest]

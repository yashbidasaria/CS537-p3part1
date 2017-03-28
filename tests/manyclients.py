import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class ManyClientsTest(servertest.ServerTest):
    name = 'manyclients'
    description = "Check that up to 16 clients can run concurrently"
    point_value = 6
    timeout = 40

    def run(self):
        key = self.findkey()
        clients = {}
        servers = {}
        s1_out = self.project_path + '/serveroutput.txt'
        s1 = self.runserver(k=key, outname=s1_out)
        servers[s1] = {'pid': s1, 'key': key, 'out': s1_out}

        # Randomly pick one client to have low priority
        p20 = random.randint(0, 15)
        priorities = [1]*16
        priorities[p20] = 19 
        time.sleep(1)

        for i in range(16):
            p = priorities[i]
            c = random.randint(3, 8)*10**8
            s = 10**9 - c
            c1 = self.runclient(k=key, p=p, c=c, s=s)
            clients[c1] ={'pid': c1, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}
            if p == 19:
                p20_pid = c1

        time.sleep(10)

        # Make sure 17th client exits gracefully
        c17 = self.runclient(k=key, p=1)
        pid, status = os.waitpid(c17, 0)
        if os.WCOREDUMP(status):
            self.fail("You shouldn't segfault!")

        time.sleep(20)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(s1_out, clients.keys())

        # Going to allow a bit of wiggle room on values since there's 17 procs
        self.check_rates(data=data, clients=clients, cnt_err=31)
        if p20_pid in data:
            low_pri = data[p20_pid][-1]['cpu']
            for pid in clients.keys():
                if pid != p20_pid and data[pid][-1]['cpu'] < low_pri:
                    self.fail("Low priority process got more cpu time than"
                              " high priority process")
            self.done()

test_list = [ManyClientsTest]

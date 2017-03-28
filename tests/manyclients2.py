import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class ManyClients2Test(servertest.ServerTest):
    name = 'manyclients2'
    description = "Check that when a client leaves, another can enter"
    point_value = 6
    timeout = 40

    def run(self):
        key = self.findkey()
        clients = {}
        servers = {}
        s1_out = self.project_path + '/serveroutput.txt'
        s1 = self.runserver(k=key, outname=s1_out)
        servers[s1] = {'pid': s1, 'key': key, 'out': s1_out}

        # Randomly pick one client to leave early
        early = random.randint(0, 15)
        time.sleep(1)

        p = 1
        for i in range(16):
            c = random.randint(3, 8)*10**8
            s = 10**9 - c
            c1 = self.runclient(k=key, p=p, c=c, s=s)
            clients[c1] ={'pid': c1, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}
            if i == early:
                early_pid = c1

        time.sleep(10)

        os.kill(early_pid, signal.SIGINT)
        time.sleep(1)

        # Make sure 17th client can run
        c = random.randint(3, 8)*10**8
        s = 10**9 - c
        c17 = self.runclient(k=key, p=p, c=c, s=s)
        clients[c17] = {'pid': c17, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}

        time.sleep(20)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(s1_out, clients.keys())

        # Going to allow a bit of wiggle room on values since there's 17 procs
        self.check_rates(data=data, clients=clients, cnt_err=29)
        self.done()

test_list = [ManyClients2Test]

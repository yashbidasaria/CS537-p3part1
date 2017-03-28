import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class TwoServersTest2(servertest.ServerTest):
    name = 'twoservers2'
    description = "Check that two servers with same key can't run concurrently"
    point_value = 6
    timeout = 10 

    def run(self):
        servers = {}
        clients = {}

        s1_out = self.project_path + '/server1output.txt'
        key = self.findkey()
        s1 = self.runserver(k=key, outname=s1_out)
        servers[s1] = {'pid': s1, 'key': key, 'out': s1_out}

        time.sleep(1)

        s2_out = self.project_path + '/server2output.txt'
        s2 = self.runserver(k=key, outname=s2_out)
        spid, status = os.waitpid(s2, 0)
        if os.WCOREDUMP(status):
            self.fail("You shouldn't segfault!")

        time.sleep(1)

        p = 1
        c = random.randint(3, 8)*10**8
        s = 10**9 - c
        c1 = self.runclient(k=key, p=p, c=c, s=s)
        clients[c1] = {'pid': c1, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}

        p = 1
        c = random.randint(2, 4)*10**8
        s = int(.5*10**9) - c
        c2 = self.runclient(k=key, p=p, c=c, s=s)
        clients[c2] = {'pid': c2, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}

        time.sleep(3)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(s1_out, clients.keys())
        self.check_rates(data=data, clients=clients)

        self.done()

test_list = [TwoServersTest2]

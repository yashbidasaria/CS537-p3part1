import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class TwoServersTest1(servertest.ServerTest):
    name = 'twoservers1'
    description = 'Check that two servers can run with different keys'
    point_value = 6
    timeout = 10 

    def run(self):
        servers = {}
        clients1 = {}
        clients2 = {}

        s1_out = self.project_path + '/server1output.txt'
        key1 = self.findkey()
        s1 = self.runserver(k=key1, outname=s1_out)
        servers[s1] = {'pid': s1, 'key': key1, 'out': s1_out}

        s2_out = self.project_path + '/server2output.txt'
        key2 = self.findkey()
        s2 = self.runserver(k=key2, outname=s2_out)
        servers[s2] = {'pid': s2, 'key': key2, 'out': s2_out}

        time.sleep(1)

        p = 1
        c = random.randint(3, 8)*10**8
        s = 10**9 - c
        c1 = self.runclient(k=key1, p=p, c=c, s=s)
        clients1[c1] = {'pid': c1, 'key': key1, 'pri': p, 'cpu': c, 'sleep': s}

        p = 1
        c = random.randint(2, 4)*10**8
        s = .5*10**9 - c
        c2 = self.runclient(k=key2, p=p, c=c, s=s)
        clients2[c2] = {'pid': c2, 'key': key2, 'pri': p, 'cpu': c, 'sleep': s}


        time.sleep(3)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(s1_out, clients1.keys())
        self.check_rates(data=data, clients=clients1)

        data = self.checkformat(s2_out, clients2.keys())
        self.check_rates(data=data, clients=clients2)

        self.done()

test_list = [TwoServersTest1]

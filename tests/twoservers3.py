import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class TwoServersTest3(servertest.ServerTest):
    name = 'twoservers3'
    description = "Check that two servers with same key can run in sequence"
    point_value = 6
    timeout = 20 

    def run(self):
        key = self.findkey()
        for i in range(2):
            servers = {}
            clients = {}

            s1_out = self.project_path + '/server1output.txt'
            s1 = self.runserver(k=key, outname=s1_out)
            servers[s1] = {'pid': s1, 'key': key, 'out': s1_out}

            time.sleep(1)

            p = 1
            c = random.randint(3, 8)*10**8
            s = 10**9 - c
            c1 = self.runclient(k=key, p=p, c=c, s=s)
            clients[c1] ={'pid': c1, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}

            time.sleep(3)
            if self.killall():
                self.fail('Failed to gracefully exit process after SIGINT')
            time.sleep(1)

            data = self.checkformat(s1_out, clients.keys())
            self.check_rates(data=data, clients=clients)

        self.done()

test_list = [TwoServersTest3]

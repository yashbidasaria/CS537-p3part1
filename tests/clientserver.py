import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class ClientServerTest(servertest.ServerTest):
    name = 'clientservertest'
    description = 'Test basic functionality for one client & server'
    point_value = 6
    timeout = 10 

    def run(self):
        servers = {}
        clients = {}
        server_out = self.project_path + '/serveroutput.txt'
        key = self.findkey()
        pid = self.runserver(k=key, outname=server_out)
        servers[pid] = {'pid': pid, 'key': key}
        time.sleep(1)
        p = 1
        c = random.randint(3, 8)*10**8
        s = 10**9 - c
        pid = self.runclient(k=key, p=p, c=c, s=s)
        clients[pid] = {'pid': pid, 'key': key, 'pri': p, 'cpu': c, 'sleep': s}
        time.sleep(3)
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        time.sleep(1)

        data = self.checkformat(server_out, clients.keys())
        self.check_rates(data=data, clients=clients)
        self.done()

test_list = [ClientServerTest]

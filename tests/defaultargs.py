import toolspath
from testing import Test
import servertest
import os
import random
import signal
import time

class DefaultArgsTest(servertest.ServerTest):
    name = 'defaultargstest'
    description = 'Test that client chooses default values for unspecified args'
    point_value = 6
    timeout = 10 

    def run(self):
        servers = []
        clients = []
        server_out = 'serveroutput.txt'
        key = self.findkey()
        servers.append(self.runserver(k=key, outname=server_out))
        time.sleep(1)
        clients.append(self.runclient(k=key))
        time.sleep(3)
        for client_pid in clients:
            os.kill(client_pid, signal.SIGINT)
        for server_pid in servers:
            os.kill(server_pid, signal.SIGINT)
        time.sleep(1)

        lines = self.checkformat(server_out, clients)
        self.done()

test_list = [DefaultArgsTest]

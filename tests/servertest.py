import toolspath
from testing import Test
import os
import random
import signal
import subprocess
import sys
import time

class ServerTest(Test):
    keys = []
    pids = []

    # Check if this key is already being used on this machine
    def keyexists(self, key):
        cmd = ['ipcs', '-m']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output = proc.stdout.read()
        if '0x%0.8x' % key in output:
            return True
        return False
        
    # Find a nonexisting key to use
    def findkey(self):
        while True:
            key = random.randint(1, 10000)
            if not self.keyexists(key):
                self.keys.append(key)
                return key

    # Remove all keys found by findkey
    def remkeys(self):
        cleanupFail = False
        for key in self.keys:
            if self.keyexists(key):
                cleanupFail = True
                cmd = ['ipcrm', '-M', str(key)]
                subprocess.call(cmd)
        return cleanupFail

    # Kill all processes started by the tests
    def killall(self):
        exitFail = False
        for pid in self.pids:
            try:
                os.kill(pid, signal.SIGINT)
            except Exception as e: # in case a process already stopped running
                pass
        time.sleep(1)
        for pid in self.pids:
            try:
                rc, status = os.waitpid(pid, os.WNOHANG)
                if rc == 0 and status == 0:
                    exitFail = True
                    os.kill(pid, signal.SIGTERM)
                elif os.WIFEXITED(status):
                    if WCOREDUMP(status):
                        exitFail = True
                else:
                    exitFail = True
                    os.kill(pid, signal.SIGTERM)
            except Exception as e:
                "exception: ", e
                pass
        return exitFail

    # Overridden for cleanup
    def done(self):
        if self.killall():
            self.fail('Failed to gracefully exit process after SIGINT')
        if self.remkeys():
            self.fail('Failed to remove shared memory page after done using it')
        super(ServerTest, self).done()

    # Overridden for cleanup
    def fail(self, message):
        self.killall()
        self.remkeys()
        super(ServerTest, self).fail(message)

    def runserver(self, k=1, cmd=None, path='stats_server', outname='output.txt'):
        # Build command to run (could have valgrind passed in, hence +=)
        path = self.project_path + '/' + path
        if cmd is None:
            cmd = [path, '-k', str(k)]
        else:
            cmd += [path, '-k', str(k)]
 
        # Run server as child proc & return its pid to caller
        print "running server with:", ' '.join(cmd)
        pid = os.fork()
        if pid == 0:
            os.close(1)
            fd = open(outname, 'w+')
            rc = os.execv(cmd[0], cmd)
            if rc != 0:
                self.fail("exec failed with status: " + str(rc))
        elif pid > 0:
            self.pids.append(pid)
            return pid
        else:
            self.fail("Forking failed")

    def runclient(self, k=1, cmd=None, p=None, s=None,c=None,path='stats_client'):
        # Have to be able to load in .so from right location
        if 'LD_LIBRARY_PATH' in os.environ.keys():
            os.environ['LD_LIBRARY_PATH'] = self.project_path + ':' + os.environ['LD_LIBRARY_PATH']
        else:
            os.environ['LD_LIBRARY_PATH'] = self.project_path
        # Build command to run
        path = self.project_path + '/' + path
        if cmd is None:
            cmd = [path]
        else:
            cmd += [path]
        opts = [['-k', str(k)]]
        if p is not None:
            opts.append(['-p', str(p)])
        if s is not None: 
            opts.append(['-s', str(s)])
        if c is not None:
            opts.append(['-c', str(c)])

        # Make sure students can handle options in any order
        random.shuffle(opts)
        for opt in opts:
            cmd += opt

        # Run client as child proc & return its pid to caller
        print "running client with:", ' '.join(cmd)
        pid = os.fork()
        if pid == 0:
            rc = os.execv(cmd[0], cmd)
            if rc != 0:
                self.fail("exec failed with status: " + str(rc))
        elif pid > 0:
            self.pids.append(pid)
            return pid
        else:
            self.fail("Forking failed")

    # Check that rates fall within an acceptable threshold
    def check_rates(self, data, clients, cnt_err=1, cpu_err=.1, start=0):
        for key in clients:
            # Supress duplicate failure messages from this function
            if self.is_failed():
                continue

            if key not in data:
                self.fail("failed to display stats correctly for pid: "
                          + str(key))
                continue
            client = clients[key]

            # Make sure count increases at reasonable rate over all
            cnt1 = data[key][0]['cnt']
            cnt2 = data[key][-1]['cnt']
            true = float(cnt2 - cnt1)

            ideal_rate = float(10**9)/float(client['cpu'] + client['sleep'])
            n_iter = data[key][-1]['time'] - data[key][0]['time']
            ideal = ideal_rate*n_iter
            if abs(ideal - true) > cnt_err:
                self.fail("count doesn't increase at correct rate")


            # Make sure cpu seconds increase at reasonable rate
            prevs = data[key][start:-1]
            currs = data[key][start + 1:]
            for prev, curr in zip(prevs, currs):
                # Supress duplicate failure messages from this function
                if self.is_failed():
                    continue
                y0 = prev['cpu']
                dx = curr['cnt'] - prev['cnt']
                dy = (float(client['cpu'])/10**9)*dx
                ideal_cpu = dy + y0    
                err = cpu_err*dy + .01 # Allow some error

                if abs(ideal_cpu - curr['cpu']) > err:
                    self.fail("cpu seconds doesn't increase at correct rate")

    # Lots of stuff to check so that format is as specified in proj description
    def checkformat(self, outname, validpids):
        # Print output first, before failing
        with open(outname, 'r') as f:
            print "server output:"
            hasline = False
            lastTime = -1 
            pids = []
            lastcpu = {}
            lastcnt = {}
            lastpri = {}
            lines = {}
            lastblank = True
            for line in f:
                # Give them their output
                print line,

                # Supress duplicate failure messages from this function
                if self.is_failed():
                    continue

                # Check if this is a data line or blank
                data = line.split()
                if len(data) == 6:
                    hasline = True
                elif len(data) > 0:
                    self.fail('incorrect number of fields in server output')
                    hasline = True
                    continue
                else:
                    lastblank = True
                    continue

                # Input validation
                try:
                    time = int(data[0])
                    pid = int(data[1])
                    argv = str(data[2])
                    cnt = int(data[3])
                    cpu = float(data[4])
                    pri = int(data[5])
                except Exception as e:
                    self.fail(str(e))
                    continue

                # Check server iteration field
                if time < lastTime:
                    self.fail("iteration numbers are decreasing in server")
                if time > lastTime:
                    if not lastblank:
                        self.fail("print \\n after each server iteration")
                if time == lastTime:
                    if lastblank:
                        self.fail("extra \\n within same server iteration")
                lastblank = False
                lastTime = time

                # Register new pid w/ its current priority
                if pid not in validpids:
                    self.fail("client pid is wrong")
                if pid not in pids:
                    pids.append(pid)
                    lines[pid] = []
                    lastcpu[pid] = 0
                    lastcnt[pid] = 0
                    lastpri[pid] = pri 

                # Check priority field stays constant
                if pri != lastpri[pid]:
                    self.fail("process' priority changed")

                # Check argv[0] field
                if len(argv) > 15:
                    self.fail("argv[0] has > 15 characters displayed")
                if len(self.project_path + '/') >= 15:
                    if argv not in self.project_path + '/':
                        self.fail("argv[0] isn't correct value")
                else:
                    if self.project_path + '/' not in argv:
                        self.fail("argv[0] isn't correct value")

                # Check count field
                if cnt < lastcnt[pid]:
                    self.fail("process' count decreased")

                # Check cpu field
                if len(data[4]) - data[4].find('.') > 3:
                    self.fail("too many decimal places")
                if cpu < lastcpu[pid]:
                    self.fail("proccess' cpu decreased")
                
                # To return lines to caller in convenient format
                dline = {}
                dline['time'] = time
                dline['pid'] = pid
                dline['argv'] = argv
                dline['cnt'] = cnt
                dline['cpu'] = cpu
                dline['pri'] = pri
                lines[pid].append(dline)

            # Verify we actually got some output from server
            if not hasline and not self.is_failed():
                self.fail("no valid output from server")
        subprocess.call(['rm', '-f', outname]) #cleanup
        # return as dict for convenient test specific processing
        return lines

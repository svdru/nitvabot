# -*- coding: utf-8 -*-

# S9 test and manage tool

import socket
import s9api
import config
import tools
from cgminer import CgminerAPI

class S9Manager(object):
    """ S9 test and manage wrapper. """

    def __init__(self, s9num):
        self.s9num = s9num
        # miner info
        self.info = {}
        # current state
        self.state = 'none'
        # dict of check results
        self.test = {}
        # last error time
        self.errorTime = 0 # import datetime. now = datetime.datetime.now().

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.
        >>> miner = S9Manager()
        >>> miner.TestAttrs()
        """

        def out(arg=None):
            return self.command(attr, arg)

        return out

    def Check(self):
        """ Check miner and make needed action """

        def Fix(testresult):
            # remember test result of step
            self.test[self.step] = testresult
            return testresult

        def TestExist():
            self.step = 'TestExist'
            try:
                socket.gethostbyaddr(s9api.getIP(self.s9num))
                return True
            except socket.gaierror:
                return False

        def TestHashrate():
            self.step = 'TestHashrate'
            try:
                # get miner status to dict
                self.info = s9api.getMinerStatus(self.s9num)
                # add miner options to dict
                self.info.update(s9api.getMinerOptions(self.s9num))
                # check GHs
                return self.info['ghs'] > 13000
            except Exception:
                return False

        def TestOptions():
            self.step = 'TestOptions'
            return (self.info['pool'] == config.POOL) and (self.info['name'] == config.WORKER)

        def TestInternet():
            self.step = 'TestInternet'
            try:
                socket.gethostbyaddr('www.ya.ru')
                return True
            except socket.gaierror:
                return False

        if self.IsValid():
            if Fix(TestExist):
                if Fix(TestHashrate):
                    if Fix(TestOptions):
                        if Fix(TestInternet):
                            return True
                        elif: Quit
                    elif: Quit
                elif: Restart
            elif: return False
        elif: return False

    def Quit(self):
        try:
            if s9api.QuitMiner(self.s9num):
                self.Validate('quited')
            else:
                self.Invalidate # mark as invalid for time delay
        except Exception:
            self.Invalidate # mark as invalid for time delay

    def Restart(self):
        try:
            if s9api.RestartMiner(self.s9num):
                self.Validate('restarted')
            else:
                self.Invalidate # mark as invalid for time delay
        except Exception:
            self.Invalidate # mark as invalid for time delay

    def Invalidate(self):
        self.state = 'invalid'
        self.errorTime = tools.Now

    def Validate(self, state):
        self.state = state
        self.stateTime = tools.Now

    def IsValid(self):
        if (self.state == 'restarted'):
            return tools.GetSecondsAfter(self.stateTime) > 300
        elif (self.state == 'quited'):
            return False
        else:
            return (self.errorTime == 0) or (tools.GetSecondsAfter(self.errorTime) > 300)

s9 = S9Manager(1)
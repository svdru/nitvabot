# -*- coding: utf-8 -*-

# S9 test and manage tool

import socket
import s9api
import config
import tools
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = __name__ + '.log')
# Setup individual logger for this module
logger = logging.getLogger(__name__)

# define class for miner manage
class S9Manager(object):
    """ S9 test and manage wrapper. """

    def __init__(self, s9num):
        self.s9num = s9num
        # miner info
        self.info = {}
        # current state
        self.state = ''
        # current check step
        self.step = ''
        # dict of check results
        self.test = {} # not used
        # last error time
        self.errorTime = 0 # import datetime. now = datetime.datetime.now().

    def Check(self):
        """ Check miner and make needed action """

        # remember test result of step
        def Fix(testFunc):
            res = testFunc()
            self.test[self.step] = res
            return res

        def TestExist():
            self.step = 'TestExist'
            try:
                socket.gethostbyaddr(s9api.getIP(self.s9num))
                return True
            except socket.herror:
                return False

        def TestInternet():
            self.step = 'TestInternet'
            try:
                socket.gethostbyaddr('www.ya.ru')
                return True
            except socket.herror:
                return False

        def TestOptions():
            self.step = 'TestOptions'
            try:
                # add miner options to dict
                self.info.update(s9api.getMinerOptions(self.s9num))
                # check options
                return (self.info['pool'] == config.POOL) and (self.info['name'] == config.WORKER)
            except Exception:
                return False

        def TestHashrate():
            self.step = 'TestHashrate'
            try:
                # add miner status to dict
                self.info.update(s9api.getMinerStatus(self.s9num))
                # check GHs
                return self.info['ghs'] > 13000
            except Exception:
                return False

        ### check LOGIC ###
        if self.IsValid():
            if Fix(TestExist):
                if Fix(TestInternet):
                    if Fix(TestOptions):
                        if Fix(TestHashrate):
                            return True # all ok
                        else:
                            self.Restart # or start after pause
                    else:
                        self.Quit # bad options, need human
                else:
                    self.Pause  # temporary quit because no internet
            else:
                return False # no miner by IP
        else:
            return False # already quited or wait for delay before check

    # выключение
    def Quit(self):
        try:
            if s9api.QuitMiner(self.s9num):
                self.Validate('quited')
            else:
                self.Invalidate('Quit') # mark as invalid for time delay
        except Exception:
            self.Invalidate('Quit') # mark as invalid for time delay

    # временное выключение
    def Pause(self):
        try:
            if s9api.QuitMiner(self.s9num):
                self.Validate('paused')
            else:
                self.Invalidate('Pause')  # mark as invalid for time delay
        except Exception:
            self.Invalidate('Pause')  # mark as invalid for time delay

    def Restart(self):
        try:
            if s9api.RestartMiner(self.s9num):
                self.Validate('restarted')
            else:
                self.Invalidate('Restart') # mark as invalid for time delay
        except Exception:
            self.Invalidate('Restart') # mark as invalid for time delay

    # Action fail
    def Invalidate(self, action):
        self.state = 'invalid'
        self.errorTime = tools.Now
        logger.warning('ASIC #%d %s failed after %s', self.s9num, action, self.step)

    # Action succesfull
    def Validate(self, state):
        self.state = state
        self.stateTime = tools.Now
        logger.warning('ASIC #%d succesfull %s after %s', self.s9num, state, self.step)

    def IsValid(self):
        if (self.state in ['restarted', 'paused']):
            return tools.GetSecondsAfter(self.stateTime) > 300
        elif (self.state == 'quited'):
            return False
        else:
            return (self.errorTime == 0) or (tools.GetSecondsAfter(self.errorTime) > 300)

s9 = S9Manager(1)
print(s9.Check())
print(s9.step)
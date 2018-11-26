# -*- coding: utf-8 -*-

# S9 test and manage tool

import socket
import s9api
import config
import tools
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename = 's9manager.log')
# Setup individual logger for this module
logger = logging.getLogger()

# Setup max failed quit/restart attempts
MAX_ATTEMPT = 5  # type: int
# Setup delay
DELAY_SECONDS = 600

# define class for miner manage
class S9Manager(object):
    """ S9 test and manage wrapper. """

    def __init__(self, num):
        self.num = num
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
        # count of iterations with error
        self.errorCount = 0

    def Check(self):
        """ Check miner and make needed action """

        # remember test result of step
        def Fix(testFunc):
            res = testFunc()
            self.test[self.step] = res
            return res

        def TestExist():
            self.step = 'TestExist'
            return s9api.IsMinerExist(self.num)

        def TestInternet():
            self.step = 'TestInternet'
            try:
                socket.gethostbyname('ya.ru')
                return True
            except socket.gaierror:
                return False

        def TestOptions():
            self.step = 'TestOptions'
            try:
                # add miner options to dict
                self.info.update(s9api.getMinerOptions(self.num))
                # check options
                return (self.info['pool'] == config.POOL) and (self.info['name'] == config.WORKER)
            except Exception:
                return False

        def TestHashrate():
            self.step = 'TestHashrate'
            try:
                # add miner status to dict
                self.info.update(s9api.getMinerStatus(self.num))
                # check GHs
                return self.info['ghs'] > 13000
            except Exception:
                return False

        ### check LOGIC ###
        if self.IsValid():
            if Fix(TestExist):
                if Fix(TestInternet):
                    if Fix(TestHashrate):
                        if Fix(TestOptions):
                            return True # all ok
                        else:
                            self.Stop()  # bad options, quit and wait for human
                    else:
                        self.Restart()  # or start after pause
                else:
                    self.Pause()  # temporary quit because no internet
            else:
                logger.warning('ASIC #%d not found', self.num)
                return False # no miner by IP
        else:
            return False # already quited or wait for delay before check

    # выключение
    def Stop(self):
        if self.state != 'stop':
            self.Process(s9api.stopMiner(self.num), 'stop')

    # временное выключение
    def Pause(self):
        if self.state != 'pause':
            self.Process(s9api.stopMiner(self.num), 'pause')

    def Restart(self):
        if self.errorCount > MAX_ATTEMPT:
            self.Stop() # to many times to try restart
        else:
            self.Process(s9api.restartMiner(self.num), 'restart')

    # Action result processing
    def Process(self, result, action):
        # Action succesfull
        if result['STATUS']:
            self.state = action
            self.errorTime = 0
            self.errorCount = 0
            logger.info('ASIC #%d %s succesfull after %s', self.num, action, self.step)
        # Action fail
        else:
            self.state = 'invalid'
            self.errorTime = tools.Now() # for time delay before next check
            self.errorCount += 1
            logger.warning('ASIC #%d %s failed after %s (%s)', self.num, action, self.step, result['ERROR'])

    # Indicate - is it possible to check
    def IsValid(self):
               # not quited early            existed or not checked yet - self.test.get('TestExist', True) and \
        return self.state != 'stop' and \
               (self.errorTime == 0 or tools.GetSecondsAfter(self.errorTime) > DELAY_SECONDS) # passed 10 min after last attempt

# execute module
if __name__ == '__main__':
    print('Запущен бесконечный цикл контроля майнеров с интервалом в %d минут' % (DELAY_SECONDS/60))
    s9list = []
    for i in range(1, 22):
        s9list.append(S9Manager(i))

    while True:
        # cycled check
        for s9 in s9list:
            s9.Check()
        # delay 5 min
        tools.Sleep(DELAY_SECONDS)
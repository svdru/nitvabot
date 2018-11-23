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
MAX_ATTEMPT = 5
# Setup delay
DELAY_SECONDS = 300

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
                            self.Quit  # bad options, quit and wait for human
                    else:
                        self.Restart  # or start after pause
                else:
                    self.Pause  # temporary quit because no internet
            else:
                logger.warning('ASIC #%d not found', self.num)
                return False # no miner by IP
        else:
            return False # already quited or wait for delay before check

    # выключение
    def Quit(self):
        if self.state == 'quit':
            return # already quited

        try:
            result = True #s9api.QuitMiner(self.num)
        except Exception:
            result = False

        self.Process(result, 'quit')

    # временное выключение
    def Pause(self):
        if self.state == 'pause':
            return # already paused

        try:
            result = True #s9api.QuitMiner(self.num)
        except Exception:
            result = False

        self.Process(result, 'pause')

    def Restart(self):
        if self.errorCount > MAX_ATTEMPT:
            self.Quit

        try:
            result = True #s9api.RestartMiner(self.num)
        except Exception:
            result = False

        self.Process(result, 'restart')


    # Action result processing
    def Process(self, result, action):
        # Action succesfull
        if result:
            self.state = action
            self.errorTime = 0
            self.errorCount = 0
            logger.warning('ASIC #%d %s succesfull after %s', self.num, action, self.step)
        # Action fail
        else:
            self.state = 'invalid'
            self.errorTime = tools.Now # for time delay before next check
            self.errorCount += 1
            logger.warning('ASIC #%d %s failed after %s', self.num, action, self.step)

    # Indicate - is it possible to check
    def IsValid(self):
               # not quited early            existed or not checked yet - self.test.get('TestExist', True) and \
        return self.state != 'quit' and \
               (self.errorTime == 0 or tools.GetSecondsAfter(self.errorTime) > DELAY_SECONDS) # passed 5 min after last attempt

# execute module
if __name__ == '__main__':
    print('Запущен бесконечный цикл контроля майнеров с интервалом в 5 минут')
    s9list = []
    for i in range(1, 22):
        s9list.append(S9Manager(i))

    while True:
        # cycled check
        for s9 in s9list:
            s9.Check()
        # delay 5 min
        tools.Sleep(DELAY_SECONDS)
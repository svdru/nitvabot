# -*- coding: utf-8 -*-

# S9 test and manage tool

import s9api
import router
import config
import tools
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename='s9manager.log')
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
        # last error time
        self.errorTime = 0
        # count of iterations with error
        self.errorCount = 0

    def check(self):
        """ Check miner and make needed action """

        def testExist():
            self.step = 'TestExist'
            return s9api.isMinerExist(self.num)

        def testInternet():
            self.step = 'TestInternet'
            return router.testInternet()

        def testOptions():
            self.step = 'TestOptions'
            try:
                # add miner options to dict
                self.info.update(s9api.getMinerOptions(self.num))
                # check options
                return (self.info['pool'] == config.POOL) and (self.info['name'] == config.WORKER)
            except:
                return False

        def testHashrate():
            self.step = 'TestHashrate'
            try:
                # add miner status to dict
                self.info.update(s9api.getMinerStatus(self.num))
                # check GHs
                return self.info['ghs'] > 13000
            except:
                return False

        # check LOGIC #
        if self.isValid():
            if testExist:
                if testInternet:
                    if testHashrate:
                        if testOptions:
                            return True  # all ok
                        else:
                            self.stop()  # bad options, quit and wait for human
                    else:
                        self.restart()  # or start after pause
                else:
                    self.pause()  # temporary quit because no internet
            else:
                logger.warning('ASIC #%d not found', self.num)
                return False  # no miner by IP
        else:
            return False  # already quited or wait for delay before check

    # выключение
    def stop(self):
        if self.state != 'stop':
            self.process(s9api.stopMiner(self.num), 'stop')

    # временное выключение
    def pause(self):
        if self.state != 'pause':
            self.process(s9api.stopMiner(self.num), 'pause')

    def restart(self):
        if self.errorCount > MAX_ATTEMPT:
            self.stop()  # to many times to try restart
        else:
            self.process(s9api.restartMiner(self.num), 'restart')

    # Action result processing
    def process(self, result, action):
        # Action succesfull
        if result['STATUS']:
            self.state = action
            self.errorTime = 0
            self.errorCount = 0
            logger.info('ASIC #%d %s succesfull after %s', self.num, action, self.step)
        # Action fail
        else:
            self.state = 'invalid'
            self.errorTime = tools.now()  # for time delay before next check
            self.errorCount += 1
            logger.warning('ASIC #%d %s failed after %s (%s)', self.num, action, self.step, result['ERROR'])

    # Indicate - is it possible to check
    def isValid(self):
        # not quited early, existed or not checked yet - self.test.get('TestExist', True) and \
        return self.state != 'stop' and \
               (self.errorTime == 0 or tools.getSecondsAfter(self.errorTime) > DELAY_SECONDS) # passed 10 min after last attempt


# execute module
if __name__ == '__main__':
    print('Запущен бесконечный цикл контроля майнеров с интервалом в %d минут' % (DELAY_SECONDS/60))
    s9list = []
    for i in range(1, 22):
        s9list.append(S9Manager(i))

    while True:
        # check router
        if router.rebootIfNoInternet(logger):
            tools.sleep(60)  # wait 1 min for reboot
        # cycled check
        for s9 in s9list:
            s9.check()
        # delay 10 min
        tools.sleep(DELAY_SECONDS)
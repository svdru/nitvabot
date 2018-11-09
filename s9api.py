# -*- coding: utf-8 -*-
# https://github.com/ckolivas/cgminer/blob/master/API-README

# S9 API logic pycgminer
import math
from cgminer import CgminerAPI

def addZeroLeft(str, len):
    return str.rjust(len).replace(' ', '0')

#    ('н', 604800),  # 60 * 60 * 24 * 7
intervals = (
    ('д', 86400),    # 60 * 60 * 24
    ('ч', 3600),    # 60 * 60
    ('м', 60),
    ('с', 1),
    )

def displayTime(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{}{}".format(value, name))
    return ''.join(result[:granularity])

def getIP(num):
    return '192.168.10.2{}'.format(addZeroLeft(str(num), 2))

def getURL(num):
    return 'http://' + getIP(num) + '/cgi-bin/minerStatus.cgi'

# Get dict of main values
def getMinerStatus(num):
    # init miner
    miner = CgminerAPI(host=getIP(num))
    # get stat dict
    statDict = dict(miner.stats())
    # init result dict
    resultDict = {}
    # fill result dict
    resultDict['elapsed'] = int  (statDict['STATS'][1]['Elapsed'])
    resultDict['ghs'    ] = float(statDict['STATS'][1]['GHS 5s' ])
    resultDict['temp1'  ] = int  (statDict['STATS'][1]['temp2_6'])
    resultDict['temp2'  ] = int  (statDict['STATS'][1]['temp2_7'])
    resultDict['temp3'  ] = int  (statDict['STATS'][1]['temp2_8'])
#   resultDict['fan1'   ] = statDict['STATS'][1]['fan3'   ]
#   resultDict['fan2'   ] = statDict['STATS'][1]['fan6'   ]
    return resultDict

# Get dict of main values
def getMinerStatus2Str(num):
    d = getMinerStatus(num)

    num2Str = addZeroLeft(str(num), 2)
    minTemp = min(d['temp1'], d['temp2'], d['temp3'])
    maxTemp = max(d['temp1'], d['temp2'], d['temp3'])
    wrkTime = displayTime(d['elapsed'])

            #01: 13651 Ghs | 74-77 | 3360-4800 | 2d8h5m36s
#   return '#%s: %.f Ghs | %d-%d-%d | %d-%d | %s' % (addZeroLeft(str(num), 2), d['ghs'], d['temp1'], d['temp2'], d['temp3'], d['fan1'], d['fan2'], displayTime(d['elapsed']))
    return '#%s: %.f Ghs | %d-%d | %s' % (num2Str, d['ghs'], minTemp, maxTemp, wrkTime)

def quitMiner(num):
    return

def restartMiner(num):
    return

# Get whole status text of all miners
def getAboutMiners():
    result = []
    for num in range(1, 22):
        result.append(getMinerStatus2Str(num))
    return '\n'.join(result)


# Helpers
def get_summary(num):
    miner = CgminerAPI(host=getIP(num))
    output = miner.summary()
    output.update({"IP": getIP(num)})
    return dict(output)

def get_stat(num):
    miner = CgminerAPI(host=getIP(num))
    output = miner.command("DEVS+NOTIFY")
    output.update({"IP": getIP(num)})
    return dict(output)

def get_pools(num):
    miner = CgminerAPI(host=getIP(num))
    output = miner.pools()
    output.update({"IP": getIP(num)})
    return dict(output)

def get_stats(ip):
    miner = CgminerAPI(host=getIP(num))
    output = miner.stats()
    output.update({"IP": getIP(num)})
    return dict(output)


if __name__ == '__main__':
    print(getAllMinerStatuses())

# -*- coding: utf-8 -*-
# https://github.com/ckolivas/cgminer/blob/master/API-README

# S9 API logic pycgminer
import requests
from cgminer import CgminerAPI
from bmminer import BmminerSSH
from tools import displayTime, addZeroLeft


# get IP by ASIC num
def getIP(num):
    return '192.168.10.2{}'.format(addZeroLeft(str(num), 2))


# get URL by ASIC num
def getURL(num):
    return 'http://' + getIP(num) + '/cgi-bin/minerStatus.cgi'


# Check exist miner via http request
def isMinerExist(num):
    url = 'http://' + getIP(num)
    try:
        return requests.get(url).status_code > 0
    except:
        return False


# Get dict of status values
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

# Get dict of status values
def getMinerOptions(num):
    # init miner
    miner = CgminerAPI(host=getIP(num))
    # get stat dict
    poolDict = dict(miner.pools())
    # init result dict
    resultDict = {}
    # fill result dict
    resultDict['pool'] = str(poolDict['POOLS'][0]['URL'] ).split('.')[1] # xxx.f2pool.xxx
    resultDict['name'] = str(poolDict['POOLS'][0]['User']).split('.')[0] # nitva.xx
    return resultDict

# Get dict of main values
def getMinerStatus2Str(num):
    try:
        d = getMinerStatus(num)
    except Exception:
        num2Str = addZeroLeft(str(num), 2)
        if isMinerExist(num):
            return '#%s: **остановлен**' % (num2Str)
        else:
            return '#%s: **не доступен**' % (num2Str)
    else:
        num2Str = addZeroLeft(str(num), 2)
        minTemp = min(d['temp1'], d['temp2'], d['temp3'])
        maxTemp = max(d['temp1'], d['temp2'], d['temp3'])
        wrkTime = displayTime(d['elapsed'])

                #01: 13651 Ghs | 74-77 | 3360-4800 | 2d8h5m36s
    #   return '#%s: %.f Ghs | %d-%d-%d | %d-%d | %s' % (addZeroLeft(str(num), 2), d['ghs'], d['temp1'], d['temp2'], d['temp3'], d['fan1'], d['fan2'], displayTime(d['elapsed']))
        return '#%s: %.f Ghs | %d-%d | %s' % (num2Str, d['ghs'], minTemp, maxTemp, wrkTime)


# Stop miner via SSH
def stopMiner(num):
    # init miner
    #miner = CgminerAPI(host=getIP(num))
    # quit miner via API
    #res = dict(miner.quit())
    # get command status
    #status = res['STATUS']
    # analize
    #if status == 'BYE':
    #    return 'Restart ok'
    #else:
    #    return 'Restart fail'

    # init miner
    miner = BmminerSSH(host=getIP(num))
    # stop miner via SSH
    return dict(miner.stop())


# restart miner via SSH
def restartMiner(num):
    # init miner
    #miner = CgminerAPI(host=getIP(num))
    # restart miner via API
    #res = dict(miner.restart())
    # get command status
    #status = res['STATUS']
    # analize
    #if status == 'RESTART':
    #    return 'Restart ok'
    #elif 'Msg' in status[0]:
    #    return str(status[0]['Msg']) # whats wrong
    #elif 'description' in status[0]:
    #    return str(status[0]['description']) # whats wrong

    # init miner
    miner = BmminerSSH(host=getIP(num))
    # restart miner via SSH
    return dict(miner.restart())


# Get whole status text of all miners
def getAboutMiners():
    result = []
    for num in range(1, 22):
        result.append(getMinerStatus2Str(num))
    return '\n'.join(result)


# OLD helpers
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
    print(getAboutMiners())

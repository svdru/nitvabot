import datetime
import time

def Now():
    return datetime.datetime.now()

def GetSecondsAfter(past):
    if past != 0:
        now = datetime.datetime.now()
        delta = now - past
        return delta.total_seconds()
    else:
        return True

def Sleep(secunds):
    time.sleep(secunds)

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

def addZeroLeft(str, len):
    return str.rjust(len).replace(' ', '0')

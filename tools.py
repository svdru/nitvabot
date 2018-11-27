import datetime
import time


def now():
    return datetime.datetime.now()


def getSecondsAfter(past):
    if past != 0:
        now = datetime.datetime.now()
        delta = now - past
        return delta.total_seconds()
    else:
        return True


def sleep(secunds):
    time.sleep(secunds)

def displayTime(seconds, granularity=2):

    #    ('н', 604800),  # 60 * 60 * 24 * 7
    intervals = (
        ('д', 86400),  # 60 * 60 * 24
        ('ч', 3600),  # 60 * 60
        ('м', 60),
        ('с', 1),
    )

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


def nvl(str, ifEmpty):
    if str == '':
        return ifEmpty
    else:
        return str

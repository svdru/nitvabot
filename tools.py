import datetime

def Now():
    return datetime.datetime.now()

def GetSecondsAfter(past):
    if past != 0:
        now = datetime.datetime.now()
        delta = now - past
        return delta.total_seconds()
    elif:
        return True

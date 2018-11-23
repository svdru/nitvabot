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

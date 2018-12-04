import os
import socket
import requests


def testInternet():
    try:
        # test сокет
        socket.gethostbyname('stratum.f2pool.com')  # при снижении скорости до 2g, и возможно нужен пинг
        # test ping
        return os.system('ping -n 1 stratum.f2pool.com') == 0  # засоряет консоль результатом пинга
    except socket.gaierror:
        return False


def rebootIfNoInternet(logger):
    if not testInternet():
        return reboot(logger)
    else:
        return False


def reboot(logger):
    params = (
        ('sysCmd', 'reboot'),
        ('apply', '%D0%97%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%B8%D1%82%D1%8C'),
        ('submit-url', '%2Fsyscmd.htm'),
    )

    try:
        response = requests.post('http://admin:q@192.168.10.1/boafrm/formSysCmd', params=params)
        print(response)
        logger.info('Router rebooted (%s)', response)
        return True
    except Exception as e:
        logger.warning('Router reboot failed (%s)', e)
        return False

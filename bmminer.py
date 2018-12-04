# -*- coding: utf-8 -*-

# SSH command with bmminer
# root\@antMiner:~# shutdown now
# OR
# root\@antMiner:~# /etc/init.d/bmminer.sh stop/start/restart/force-reset

import paramiko
from tools import nvl


class BmminerSSH(object):
    """ Bmminer SSH command wrapper. """

    def __init__(self, host='localhost', user='root', password='admin'):
        self.data = {}
        self.host = host
        self.user = user
        self.password = password

    def command(self, command, arg=None):
        """ Initialize a ssh connection,
        execute command with bmminer.sh
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=self.host, username=self.user, password=self.password)
            stdin, stdout, stderr = ssh.exec_command('/etc/init.d/bmminer.sh %s' % command)
            res = stderr.read() # = stdout.read() + stderr.read()
        except Exception as e:
            return dict({'STATUS': False, 'ERROR': e})
        else:
            return dict({'STATUS': res == '', 'ERROR': nvl(res, 'OK')})
        finally:
            ssh.close()

    def __getattr__(self, attr):
        """ Allow us to make command calling methods.
        >>> bmminer = BmminerSSH()
        >>> bmminer.restart() or bmminer.stop() or bmminer.start()
        """

        def out(arg=None):
            return self.command(attr, arg)

        return out


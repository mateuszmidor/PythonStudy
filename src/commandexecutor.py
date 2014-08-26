'''
Created on 26-08-2014

@author: mateusz
'''

from subprocess import Popen, PIPE, STDOUT
import shlex

class CommandExecutor():

    @staticmethod
    def execute(cmd):
        args = shlex.split(cmd)
        proc = Popen(args=args, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=False)
        out = proc.stdout.read()
        return out
        
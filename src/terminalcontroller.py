'''
Created on 08-09-2014

@author: mateusz
'''
import logging
from commandexecutor import CommandExecutor
from terminalrenderer import TerminalRenderer

class TerminalController(object):

    def runCmd(self, args):
        cmd = self._getCommand(args)
        historyOutput = self._getHistoryOutput(args)
        self.logCommandUnderExecution(cmd)
        commandOutput = self._runCommand(cmd)
        output = self._formatOutput(historyOutput, cmd, commandOutput)
        TerminalRenderer.render(output)        

    def _runCommand(self, cmd):
        if (not cmd):
            return u""   
            
        try:
            out = CommandExecutor.execute(cmd)
            return out
        except Exception, e:
            return unicode(e) 

    def _formatOutput(self, historyOutput, cmd, commandOutput):
        return "%s%s\n%s\n" % (historyOutput, cmd, commandOutput)

    def _getCommand(self, args):
        return args.getvalue("command", u"")

    def _getHistoryOutput(self, args):
        return args.getvalue("output", u"")

    def logCommandUnderExecution(self, cmd):
        return logging.info("Running: '%s'" % cmd)





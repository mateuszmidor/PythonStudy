# -*- coding: utf-8 -*-

from onlineview import OnlineView
from commandexecutor import CommandExecutor

class Main():
    
    @staticmethod
    def run(args):
        output = args.getvalue("output", u"")
        cmd = args.getvalue("command", u"")
        out = Main.runCommand(cmd)
        output += cmd + u"\n" + out + u"\n"
        OnlineView.render(output)
        
    @staticmethod
    def runCommand(cmd):
        if (cmd):
            try:
                out = CommandExecutor.execute(cmd)
                return out
            except Exception, e:
                return unicode(e) 
        else:
            return u""
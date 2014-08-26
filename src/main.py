# -*- coding: utf-8 -*-

from onlineview import OnlineView

class Main():
    
    @staticmethod
    def run(args):
        output = args.getvalue("output", u"> ")
        cmd = args.getvalue("command", u"")
        OnlineView.render(cmd)
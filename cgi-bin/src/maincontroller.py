'''
Created on 08-09-2014

@author: mateusz
'''
import logging
import time
from src.terminalcontroller import TerminalController
from src.errorcontroller import ErrorController

class MainController(object):
    
    def __init__(self):
        self.initLogging()
        
    def run(self, params):
        try:
            self.logNewSession()
            terminal = TerminalController()
            terminal.runCmd(params)
            
        except Exception as e:
            self.logException(e)
            error = ErrorController()
            error.run()
            
        finally:
            self.logEndSession()
            
    def logNewSession(self):
        return logging.info("New session: " + time.strftime("%X, %x"))

    def logException(self, e):
        return logging.exception(str(e))

    def logEndSession(self):
        return logging.info("End session: " + time.strftime("%X, %x") + "\n")

    def initLogging(self):
        LOGGER_FILENAME = "cgi-bin/diagnostics/logger.txt"
        logging.basicConfig(filename=LOGGER_FILENAME, level=logging.INFO)





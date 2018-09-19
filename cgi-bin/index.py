#!/usr/bin/env python2

import cgi
from src.maincontroller import MainController

params = cgi.FieldStorage()
main = MainController()
main.run(params)

#!/usr/bin/python

import cgi
from src import MainController

params = cgi.FieldStorage()
main = MainController()
main.run(params)
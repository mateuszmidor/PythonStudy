'''
Created on 08-09-2014

@author: mateusz
'''
from src.webpagetemplate import WebPageTemplate
from src.httpresponse import HttpResponse

class ErrorRenderer(object):
    
    @staticmethod
    def render():
        errorPage = ErrorRenderer.getErrorPage()
        HttpResponse.renderPage(errorPage.getHtml())

    @staticmethod
    def getErrorPage():
        page = WebPageTemplate.fromFile("cgi-bin/data/Error.htm")
        return page
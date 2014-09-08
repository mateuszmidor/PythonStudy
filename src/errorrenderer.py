'''
Created on 08-09-2014

@author: mateusz
'''
from webpagetemplate import WebPageTemplate
from httpresponse import HttpResponse

class ErrorRenderer(object):
    
    @staticmethod
    def render():
        errorPage = ErrorRenderer.getErrorPage()
        HttpResponse.renderPage(errorPage.getHtml())

    @staticmethod
    def getErrorPage():
        page = WebPageTemplate.fromFile("data/Error.htm")
        return page
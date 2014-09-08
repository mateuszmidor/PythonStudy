from webpagetemplate import WebPageTemplate
from httpresponse import HttpResponse

class TerminalRenderer():
    
    @staticmethod
    def render(terminalContent):
        offerPage = TerminalRenderer.prepareOfferPage(terminalContent)
        HttpResponse.renderPage(offerPage.getHtml())

    @staticmethod
    def prepareOfferPage(contents):
        page = WebPageTemplate.fromFile("data/Terminal.htm")
        page.setField(u"$OUTPUT$", contents)
        return page


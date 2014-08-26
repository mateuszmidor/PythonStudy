from webpagetemplate import WebPageTemplate
from httpresponse import HttpResponse

class OnlineView():
    
    @staticmethod
    def render(commandLog):
        offerPage = OnlineView.getOfferPage(commandLog)
        HttpResponse.renderPage(offerPage.getHtml())

    @staticmethod
    def getOfferPage(commandLog):
        offerPage = WebPageTemplate.fromFile("data/Terminal.htm")
        offerPage.setField(u"$OUTPUT$", commandLog)
        return offerPage


from utf8printer import Utf8Printer
class HttpResponse():
    printer = Utf8Printer
    
    @staticmethod
    def renderPage(html):
        HttpResponse.printHttpContentTypeHeader() 
        HttpResponse.printContent(html)  
             
    @staticmethod
    def printHttpContentTypeHeader():
        HttpResponse.printer.printText(u"Content-type: text/html;charset=utf-8\n\n")

    @staticmethod
    def printContent(html, ):
        HttpResponse.printer.printText(html)
import web
# Mother class for all webpages
class Webpage(object):
    def __init__(self):
        self.webrender = web.template.render('templates/')
        self.title = 'subclass did not set title'
        self.body = 'subclass did not set body'
        self.header = 'class did not set header'
        self.footer = 'class did not set footer'

    # Main render loop that takes care of rendering the 'page.html'
    def render(self):
#TODO add header, footer: page_header, page_footer.html
        self.render_body()
        return self.webrender.page(self.title, self.body)

    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError


    def mauw(self):
        print 'miaaaauw miaauw'

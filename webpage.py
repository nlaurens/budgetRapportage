# Mother class for all webpages
class Webpage(object):
    def __init__(self, title):
        self.title = title

    def render(self):
        print 'rendering webpage'
        self.render_body()
        print self.title
        print self.body

# Mother class for all webpages
#class Webtest(Webpage):
#
#    def __init__(self, title):
#        Webpage.__init__(self, title)
#
#    def render_body(self):
#        print 'rendering body'
#        self.body = 'BODY RENDERED'
#

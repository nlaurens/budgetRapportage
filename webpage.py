import web
# Mother class for all webpages
class Webpage(object):
    def __init__(self, static=False):
        self.mainRender = web.template.render('templates/')
        self.static = static
        self.title = 'subclass did not set title'
        self.body = 'subclass did not set body'

    def render(self):
#TODO cache renderd page and check if we can serve that
        self.render_body()
        return self.mainRender.page(self.title, self.body)

    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError

class Simple(Webpage):
    def __init__(self, title, msg, form=''):
        Webpage.__init__(self)

        #subclass specific
        self.title = title
        self.msg = msg
        self.form = form


    def render_body(self):
        self.body = self.mainRender.simple(self.title, self.msg, self.form)

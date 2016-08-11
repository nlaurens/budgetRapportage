import web
# Mother class for all webpages
class Webpage(object):
    def __init__(self, userHash, params, static=False):
        self.userHash = userHash
        self.params = params
        self.static = static
        self.mainRender = web.template.render('templates/', cache=False) #in init cause subclasses might also access it

        # should be set in the subclass
        self.title = None
        self.module = None
        self.webrender = None


    def render(self):
#TODO cache renderd page and check if we can serve that
        self.render_body()
        return self.mainRender.page(self.title, self.body)


    def base_url(self):
        return ('/%s/%s' % (self.module, self.userHash))


    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError


# Simple webpage for messages/forms
class Simple(Webpage):
    def __init__(self, userHash, title, msg, form=''):
        Webpage.__init__(self, userHash, None)

        #subclass specific
        self.title = title
        self.msg = msg
        self.form = form


    def render_body(self):
        self.body = self.mainRender.simple(self.title, self.msg, self.form)

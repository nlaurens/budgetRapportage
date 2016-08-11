import web
from config import config
from webpage import Webpage

class Index(Webpage):
    def __init__(self, userHash):
        Webpage.__init__(self, userHash)

        #subclass specific
        self.webrender = web.template.render('templates/index/')
        self.title = 'Menu'


    def render_body(self):
        self.body = self.webrender.index(self.title, self.userHash)

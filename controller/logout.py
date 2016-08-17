from controller import Controller
import web


class Logout(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Logout'
        self.module = 'logout'
        self.webrender = web.template.render('webpages/access/')
        self.redirect = 'index'

    def process_sub(self):
        self.msg = ['You have been logged out']
        self.redirect = self.redirect
        self.body = self.render_simple()

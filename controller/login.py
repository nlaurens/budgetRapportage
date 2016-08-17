from controller import Controller
import web
from web import form


class Login(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Login'
        self.module = 'login'
        self.webrender = web.template.render('webpages/access/')
        self.redirect = web.input(caller='index').caller

        # forms
        self.form_login = form.Form(
                form.Password('password', form.notnull, value='', description='Enter Password:'),
                form.Button('Login'),
        )

    def process_sub(self):
        form_login = self.form_login
        if form_login.validates():
            if form_login['password'].value == self.config["globalPW"]:

                # TODO SESSION VAR HIER VERKRIJGEN?
                # session.logged_in = True
                self.title = 'Login succes!'
                self.msg = ['You have been logged in']
                self.msg = ['SESSION NOT YET SET!!']
                self.redirect = self.redirect
                self.body = self.render_simple()
            else:
                # wrong pw
                self.body = self.webrender.login(self.form_login) 
        else:
            # first login
            self.body = self.webrender.login(self.form_login)






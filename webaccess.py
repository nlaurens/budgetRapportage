import web
from web import form
from config import config
from webpage import Webpage

class Login(Webpage):
    def __init__(self, userHash):
        Webpage.__init__(self, userHash)

        #subclass specific
        self.title = 'Login'
        self.module = 'login'
        self.webrender = web.template.render('templates/access/')

        #login specific
        self.redirect = web.input(caller='index').caller

        #forms
        self.form_login = form.Form (
                form.Password('password', form.notnull, value='', description='Enter Password:' ),
                form.Button('Login'),
        )


    def render_body(self):
        self.body = self.webrender.login(self.form_login)


    def parse_form(self, session):
        form = self.form_login
        if form.validates():
            if form['password'].value == config["globalPW"]:
                session.logged_in = True
                raise web.seeother('/%s/%s' % (self.redirect, self.userHash))

        return False

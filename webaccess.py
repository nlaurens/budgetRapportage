import web
from config import config
from webpage import Webpage

class Login(Webpage):
    def __init__(self, userHash, params):
        Webpage.__init__(self, userHash, params)

        #subclass specific
        self.title = 'Login'
        self.module = 'login'
        self.webrender = web.template.render('templates/access/')

        #login specific
#TODO get target from params
        self.redirect = params.caller
        self.msg = ''


    def render_body(self):
        self.body = self.webrender.login(self.form_login(), self.msg)


    def form_login(self):
        form = web.form.Form (
                web.form.Password('password', web.form.notnull, value='', description='Enter Password:' ),
                web.form.Button('Login'),
        )
        return form


    def parse_form(self, session):
        form = self.form_login()
        if form.validates():
            if form['password'].value == config["globalPW"]:
                session.logged_in = True
                raise web.seeother('/%s/%s' % (self.redirect, self.userHash))
            else:
                self.msg = 'Wrong password'
        else:
            self.msg = 'Please enter a password'

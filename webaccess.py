from webpage import Webpage

class Webaccess(Webpage):
    def __init__(self, userHash, caller, subpage):
        Webpage.__init__(self)

        #subclass specific
        self.userHash = userHash
        self.caller = caller
        self.subpage = subpage


    def render_body(self):
        if self.subpage == 'login':
            self.body = self.webrender.login(self.form_login())

#TODO implement logout and the 404!
        elif self.supage == 'logout':
            self.body = 'logout'
        else:
            self.body = '404'

 
    def form_login(self):
        form = web.form.Form(
            web.form.Password('password', web.form.notnull, value=''),
            web.form.Button('Login'),
        )

        return form

    def blaf(self):
        print 'woef woef '

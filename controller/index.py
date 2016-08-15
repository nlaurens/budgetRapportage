from controller import Controller
from web import form

class Index(Controller):
    def __init__(self):
        Controller.__init__(self)
        self.form_redirect = form.Form(
                form.Button('ok', value='redirect')
        )

    def process_sub(self, userHash):
        self.title = 'Welcome'
        self.msg = 'Make a selection from the menu above.'
        self.body = self.render_simple()



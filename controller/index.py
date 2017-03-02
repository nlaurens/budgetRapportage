from controller import Controller


class Index(Controller):
    def __init__(self):
        Controller.__init__(self)
        self.title = 'Welcome'
        self.module = 'index'

    def authorized(self):
        return True

    def process_sub(self):
        msg = ['Make a selection from the menu above.']
        self.body = self.render_simple(msg)



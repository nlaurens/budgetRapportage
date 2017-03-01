from controller import Controller


class Index(Controller):
    def __init__(self):
        Controller.__init__(self)
        self.title = 'Welcome'
        self.module = 'index'
        self.msg = ['Make a selection from the menu above.']

    def process_sub(self):
        self.body = self.render_simple()



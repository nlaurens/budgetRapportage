from controller import Controller

class Index(Controller):
    def __init__(self):
        Controller.__init__(self)

    def process_sub(self):
        self.title = 'Welcome'
        self.msg = ['Make a selection from the menu above.']
        self.body = self.render_simple()



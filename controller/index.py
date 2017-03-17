from controller import Controller
from model.users import orders_allowed


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
        
        print 'haaa'
        orders = orders_allowed()
        print orders



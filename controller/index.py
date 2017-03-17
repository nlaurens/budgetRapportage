from controller import Controller
from model.users import orders_allowed
from model.users import get_username


class Index(Controller):
    def __init__(self):
        Controller.__init__(self)
        self.title = 'Welcome'
        self.module = 'index'

    def authorized(self):
        return True

    def process_sub(self):
        msg = ['User %s please make a selection from the menu above.'% get_username()]
        self.body = self.render_simple(msg)

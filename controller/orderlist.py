from config import config
from controller import Controller
import web
from web import form

import numpy as np
import model.regels
import model.ksgroup
from functions import moneyfmt
from matplotlib import cm


class Orderlist(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Orderlist'
        self.module = 'Orderlist'
        self.webrender = web.template.render('webpages/orderlist/')

    def process_sub(self):
        orderlist = {}
        orderlist['items'] = model.orderlist.load()
        self.body = self.webrender.orderlist(orderlist)
        return


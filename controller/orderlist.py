from config import config
from controller import Controller
import web
from web import form

import numpy as np
import model.orders
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
        orderlist = model.orders.load()
        #TODO add option to sort by budgethouder as well.
        orderlist_per_actcode = orderlist.split(['activiteitencode'])
        tables = []
        for code, orderlist_dict in orderlist_per_actcode.iteritems():
            tables.append(code)

        self.body = self.webrender.orderlist(tables)
        return


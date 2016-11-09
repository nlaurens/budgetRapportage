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
        for code, orderlist_per_code in orderlist_per_actcode.iteritems():
            header = {'id':code, 'name':'Activiteiten code '+ str(code)}
            table_items = []
            for order in orderlist_per_code.orders:
                item = {}
                item['order'] = order.ordernummer
                item['omschrijving'] = order.ordernaam
                item['budgethouder'] = order.budgethouder
                item['activiteitenhouder'] = order.activiteitenhouder
                item['sub.act.code'] = order.subactiviteitencode
                table_items.append(item)

            tables.append(self.webrender.table(table_items, header))

        #TODO javascripts for +/- collapse button
        javascripts = self.webrender.javascripts(orderlist_per_actcode.keys())
        self.body = self.webrender.orderlist(tables, javascripts)
        return


import web

import model.orders
from controller import Controller


class Orderlist(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Orderlist'
        self.module = 'Orderlist'
        self.webrender = web.template.render('webpages/orderlist/')

    def authorized(self):
        return model.users.check_permission(['orderlist'])

    def process_sub(self):
        orders_allowed = model.users.orders_allowed()
        orderlist = model.orders.load(orders_load=orders_allowed)

        orderlist_per_actcode = orderlist.split(['activiteitencode'])
        tables = []

        for code, orderlist_per_code in orderlist_per_actcode.iteritems():
            header = {'id': code, 'name': 'Activiteiten code ' + str(code)}
            table_items = []
            for order in orderlist_per_code.orders:
                item = {}
                item['order'] = order.ordernummer
                item['omschrijving'] = order.ordernaam
                item['budgethouder'] = order.budgethouder
                item['sub.act.code'] = order.subactiviteitencode
                item['link'] = self.url(module='view', params={'order': order.ordernummer})
                table_items.append(item)

            tables.append(self.webrender.table(table_items, header))

        javascripts = self.webrender.javascripts(orderlist_per_actcode.keys())
        self.body = self.webrender.orderlist(tables, javascripts)
        return

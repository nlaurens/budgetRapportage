import web
import numpy as np
from web import form

from controller import Controller
from functions import table_string

import model.ordergroup
import model.regels

class Salaris(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Salaris'
        self.module = 'salaris'
        self.webrender = web.template.render('webpages/salaris/')

        # Salaris specific:
        self.ordergroup_file = str(web.input(ordergroep='LION')['ordergroep'])
        ordergroup = model.ordergroup.load(self.ordergroup_file)
        self.ordergroup = ordergroup.find(str(web.input(subgroep='TOTAAL')['subgroep']))
        self.orders = self.ordergroup.list_orders_recursive().keys()


    def process_sub(self):
        regels = model.regels.load(table_names_load=['salaris_plan', 'salaris_geboekt', 'salaris_obligo'],orders_load=self.orders)
        data = self.create_data_structure(regels)

        report = {}
        report['settings'] = self.render_settings()
        report['summary'] = self.render_summary(data)
        report['body'] = self.render_body(data)
        report['javaScripts'] = self.webrender.salaris_javascripts(data['orders'].keys())

        self.body = self.webrender.salaris(report)


    """
    Returns 'data' (dict) needed to build the webpage. Not we use the payrollnr
    as the key as they are unique per person while a single person might have 
    multiple contracts and hence personeelsnummers.

    data-structure for total overview:
      data['totals']           = {'begroot/realisatie/obligo/resultaat' as decimal, ..}
      data['payrollnrs'][<payrollnr>] = {'begroot/realisatie/obligo/resultaat' as decimal,
                                         'naam' as string, 'realiatie-perc' as decimal, 
                                         'match' as Boolean that is True if begroot/realisatie could be coupled via payroll/persnr}

    data-structure for overview per order:
      data['orders'][<ordernummer>] = {'naam' as string, ..}
      data['orders'][<ordernummer>]['totals'] = {'begroot/realisatie/obligo/resultaat' as decimal'}

      data['orders'][<ordernummer>]['payrollnrs'][<payrollnr>] = {'match' as Boolean (True if begroot and realisatie/obligo on the correct order),
                                                                  'begroot/realisatie/obligo/resultaat' as decimal, 
                                                                  'naam' as string, 'realiatie-perc' as decimal}

    """
    def create_data_structure(self, regels):
        data = { 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}, 'orders':{}, 'payrollnrs':{} }  

        obligo = regels.split(['tiepe', 'personeelsnummer'])['salaris_obligo'] 
        payroll_map = self.payroll_map(obligo)

        regels_per_order = regels.split(['ordernummer'])
        for order, regelList in regels_per_order.iteritems():
            if order not in data['orders']:
                data['orders'][order] = { 'naam':'TODO NAAM ORDER', 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}, 'payrollnrs':{} }  

            for regel in regelList.regels:
                match = False
                if regel.tiepe == 'salaris_geboekt' or regel.tiepe == 'salaris_plan':  
                    if regel.personeelsnummer in payroll_map:
                        payrollnr = payroll_map[regel.personeelsnummer]
                        match = True
                    else:
                        payrollnr = regel.personeelsnummer
                else:
                    payrollnr = regel.payrollnummer

                # data - order - payroll
                if payrollnr not in data['orders'][order]['payrollnrs']:
                    data['orders'][order]['payrollnrs'][payrollnr] = {'naam':regel.personeelsnaam, 'match':match, 'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}
                data['orders'][order]['payrollnrs'][payrollnr]['match'] = match or data['orders'][order]['payrollnrs'][payrollnr]['match']  # once it is true it should stay true
                data['orders'][order]['payrollnrs'][payrollnr][regel.tiepe] += regel.kosten
                data['orders'][order]['payrollnrs'][payrollnr]['resultaat'] = data['orders'][order]['payrollnrs'][payrollnr]['salaris_plan'] - data['orders'][order]['payrollnrs'][payrollnr]['salaris_geboekt'] - data['orders'][order]['payrollnrs'][payrollnr]['salaris_obligo']
                if data['orders'][order]['payrollnrs'][payrollnr]['salaris_plan'] > 0:
                    data['orders'][order]['payrollnrs'][payrollnr]['resultaat_perc'] = data['orders'][order]['payrollnrs'][payrollnr]['salaris_geboekt'] / data['orders'][order]['payrollnrs'][payrollnr]['salaris_plan']
                else:
                    data['orders'][order]['payrollnrs'][payrollnr]['resultaat_perc'] = 0

                # data - order - totals
                data['orders'][order]['totals'][regel.tiepe] += regel.kosten
                data['orders'][order]['totals']['resultaat'] = data['orders'][order]['totals']['salaris_plan'] - data['orders'][order]['totals']['salaris_geboekt'] - data['orders'][order]['totals']['salaris_obligo']

                # data - totals
                data['totals'][regel.tiepe] += regel.kosten
                data['totals']['resultaat'] = data['totals']['salaris_plan'] - data['totals']['salaris_geboekt'] - data['totals']['salaris_obligo']

                # data - payroll
                if payrollnr not in data:
                    data['payrollnrs'][payrollnr] = {'naam':regel.personeelsnaam, 'match':match, 'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}
                data['payrollnrs'][payrollnr]['match'] = match or data['payrollnrs'][payrollnr]['match']  # once it is true it should stay true
                data['payrollnrs'][payrollnr][regel.tiepe] += regel.kosten
                data['payrollnrs'][payrollnr]['resultaat'] = data['payrollnrs'][payrollnr]['salaris_plan'] - data['payrollnrs'][payrollnr]['salaris_geboekt'] - data['payrollnrs'][payrollnr]['salaris_obligo']
                if data['payrollnrs'][payrollnr]['salaris_plan'] > 0:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = data['payrollnrs'][payrollnr]['salaris_geboekt'] / data['payrollnrs'][payrollnr]['salaris_plan']
                else:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = 0

        return data

    """
    construct hash_map for payroll to personeelsnummers
        note that payroll nummers will always have 1 personeelsnummer
        while multiple personeelsnummers (contracts) may refer to
        a single payrollnumber
    """ 
    def payroll_map(self, regels_obligo):
        # { 'persnr': payrollnummer }
        payroll_map = {}
        for persnr, regelList in regels_obligo.iteritems():
            for regel in regelList.regels:
                if persnr not in payroll_map:
                    payroll_map[persnr] = regel.payrollnummer
                else:
                    if regel.payrollnummer != payroll_map[persnr]:
                        print 'ERRROR, multiple payrollnumbers for a single personeelsnummer'
                        print persnr
                        print regel.payrollnummer
                        exit()

        return payroll_map


    def render_body(self, data):
        order_tables = []
        for order in data['orders'].keys():
            header = {}
            header['id'] = order
            header['userHash'] = 'todo USERHASH'
            header['img'] = '../static/figs/TODO.png'
            header['name'] = data['orders'][order]['naam'] + ' - ' + str(order)
            header['ordernaam'] = data['orders'][order]['naam']
            header['begroot'] = table_string(data['orders'][order]['totals']['salaris_plan'])
            header['geboekt'] = table_string(data['orders'][order]['totals']['salaris_geboekt'])
            header['obligo'] = table_string(data['orders'][order]['totals']['salaris_obligo'])
            header['resultaat'] = table_string(data['orders'][order]['totals']['resultaat'])

            table_items = []
            for key in data['orders'][order]['payrollnrs'].keys():
                row = data['orders'][order]['payrollnrs'][key]
                html = {}
                html['naam'] = row['naam']
                html['personeelsnummer'] = key  #TODO: on mouseover show all personeelsnummers that are linked to this number
                html['begroot'] = table_string(row['salaris_plan'])
                html['geboekt'] = table_string(row['salaris_geboekt'])
                html['resultaat'] = table_string(row['resultaat'])
                html['resultaat_perc'] = '%.f' % row['resultaat_perc'] + '%'
                html['td_class'] = 'success' if row['match'] else 'danger'
                table_items.append(self.webrender.salaris_personeel_regel(html))

            order_tables.append(self.webrender.salaris_table_order(table_items, header))

        person_tables = None
        return self.webrender.salaris_body(order_tables, person_tables)

    def render_settings(self):
        # TODO add settings form
        form_settings = 'todo form met optie'
        return self.webrender.salaris_settings(form_settings)


    def render_summary(self, data):
        begroot = data['totals']['salaris_plan']
        geboekt =  data['totals']['salaris_geboekt']
        obligo = data['totals']['salaris_obligo']
        kosten = data['totals']['salaris_geboekt']
        resultaat = data['totals']['resultaat']

        html = {}
        html['begroot'] = table_string(begroot)
        html['geboekt'] = table_string(geboekt)
        html['obligo'] = table_string(obligo)
        html['resultaat'] = table_string(resultaat)
        html['totaalkosten'] = table_string(kosten)

        return self.webrender.salaris_summary(html)

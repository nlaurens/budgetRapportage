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
        report['javaScripts'] = self.webrender.salaris_javascripts(data['orders'].keys() + ['payrollnr_nomatch', 'payrollnr_nokosten','payrollnr_matched'])

        self.body = self.webrender.salaris(report)


    """
    Returns 'data' (dict) needed to build the webpage. Not we use the payrollnr
    as the key as they are unique per person while a single person might have 
    multiple contracts and hence personeelsnummers.

    data-structure for total overview:
      data['totals']           = {'begroot/realisatie/obligo/resultaat' as decimal, ..}

    data-structure for view per payrollnr:
      data['payrollnrs'][<payrollnr>] = {'begroot/realisatie/obligo/resultaat' as decimal,
                                         'naam' as string, 'realiatie-perc' as decimal, 
                                         'match' as Boolean that is True if begroot/realisatie could be coupled via payroll/persnr}

    data-structure for overview per order:
      data['orders'][<ordernummer>] = {'naam' as string, ..}
      data['orders'][<ordernummer>]['totals'] = {'begroot/realisatie/obligo/resultaat' as decimal'}

      data['orders'][<ordernummer>]['payrollnrs'][<payrollnr>] = {'match' as Boolean (True if begroot and realisatie/obligo on the correct order),
                                                                  'begroot/realisatie/obligo/resultaat' as decimal, 
                                                                  'naam' as string, 'realiatie-perc' as decimal}
    data-structure for overview per tiepe (match/nomatch/nokosten):
      data['tiepe'][<tiepe>] = {'naam' as string, ..}
      data['tiepe'][<tiepe>]['totals'] = {'begroot/realisatie/obligo/resultaat' as decimal'}

      data['tiepe'][<tiepe>]['payrollnrs'][<payrollnr>] = {'match' as Boolean (True if begroot and realisatie/obligo on the correct order),
                                                                  'begroot/realisatie/obligo/resultaat' as decimal, 
                                                                  'naam' as string, 'realiatie-perc' as decimal}

    """
    def create_data_structure(self, regels):

        obligo = regels.split(['tiepe', 'personeelsnummer'])['salaris_obligo'] 
        regels_per_order = regels.split(['ordernummer'])
        payroll_map = self.payroll_map(obligo)
        last_periode = model.regels.last_periode()
        order_list = model.orders.load().split(['ordernummer'])

        #TODO refactor initiate with deepcopy of an empty total dictionary etc.
        data = { 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}, 'orders':{}, 'payrollnrs':{}, 'match':{'payrollnrs':{}, 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}}, 'nomatch':{'payrollnrs':{}, 'totals':{'salaris_plan':0, 'salaris_obligo':0,
            'salaris_geboekt':0, 'resultaat':0}}, 'nokosten':{'payrollnrs':{}, 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}} }  
        for order, regelList in regels_per_order.iteritems():
            if order not in data['orders']:
                name = order_list[order].orders[0].ordernaam
                data['orders'][order] = { 'naam':name, 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}, 'payrollnrs':{} }  

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
                    if regel.tiepe == 'salaris_obligo' and regel.periode < last_periode:  # only allow obligos that are yet to come
                        continue

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

                # data - payroll
                if payrollnr not in data['payrollnrs']:
                    data['payrollnrs'][payrollnr] = {'naam':regel.personeelsnaam, 'match':match, 'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}
                data['payrollnrs'][payrollnr]['match'] = match or data['payrollnrs'][payrollnr]['match']  # once it is true it should stay true
                data['payrollnrs'][payrollnr][regel.tiepe] += regel.kosten
                data['payrollnrs'][payrollnr]['resultaat'] = data['payrollnrs'][payrollnr]['salaris_plan'] - data['payrollnrs'][payrollnr]['salaris_geboekt'] - data['payrollnrs'][payrollnr]['salaris_obligo']
                if data['payrollnrs'][payrollnr]['salaris_plan'] > 0:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = data['payrollnrs'][payrollnr]['salaris_geboekt'] / data['payrollnrs'][payrollnr]['salaris_plan']
                else:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = 0

        # data - match/nomatch/nokosten - ..
        for payrollnr, row in data['payrollnrs'].iteritems():
            if row['match']:
                tiepe = 'match'
            elif row['salaris_geboekt'] > 0 or row['salaris_obligo'] > 0:
                tiepe = 'nomatch'
            else:
                tiepe = 'nokosten'


            # data - match/nomatch/nokosten - payroll
            data[tiepe]['payrollnrs'][payrollnr] = row

            # data - match/nomatch/nokosten - totals
            # data - totals
            for kosten_tiepe in ['salaris_plan', 'salaris_geboekt', 'salaris_obligo', 'resultaat']:
                data[tiepe]['totals'][kosten_tiepe] += row[kosten_tiepe]
                data['totals'][kosten_tiepe] += row[kosten_tiepe]

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
        order_tables = self.render_order_tables(data)
        person_tables = self.render_person_tables(data)
        tiepe_tables = self.render_tiepe_tables(data)

        return self.webrender.salaris_body(order_tables, person_tables, tiepe_tables)


    def render_person_tables(self, data):
        return []


    def render_tiepe_tables(self, data):
        tiepe_tables = []
        table_match_items = []
        table_nomatch_items = []
        table_nokosten_items = []
        for tiepe in ['match', 'nomatch', 'nokosten']:
            for payrollnr in data[tiepe]['payrollnrs'].keys():
                row = data[tiepe]['payrollnrs'][payrollnr]
                html = {}
                html['naam'] = row['naam']
                html['personeelsnummer'] = payrollnr  #TODO: on mouseover show all personeelsnummers that are linked to this number
                html['begroot'] = table_string(row['salaris_plan'])
                html['geboekt'] = table_string(row['salaris_geboekt'])
                html['obligo'] = table_string(row['salaris_obligo'])
                html['resultaat'] = table_string(row['resultaat'])
                html['resultaat_perc'] = '%.f' % (row['resultaat_perc']*100) + '%'
                html['td_class'] = 'success' if row['match'] else 'danger'

                if tiepe == 'match':
                    table_match_items.append(self.webrender.salaris_personeel_regel(html))
                elif tiepe == 'nomatch':
                    table_nomatch_items.append(self.webrender.salaris_personeel_regel(html))
                elif tiepe == 'nokosten':
                    table_nokosten_items.append(self.webrender.salaris_personeel_regel(html))

        header_match = {}
        header_match['id'] = 'payrollnr_matched' 
        header_match['userHash'] = 'todo USERHASH'
        header_match['img'] = '../static/figs/TODO.png'
        header_match['name'] = 'Begroot en gerealiseerd'
        header_match['ordernaam'] = 'Begroot en gerealiseerd' 
        header_match['begroot'] = table_string(data['match']['totals']['salaris_plan'])
        header_match['geboekt'] = table_string(data['match']['totals']['salaris_geboekt'])
        header_match['obligo'] = table_string(data['match']['totals']['salaris_obligo'])
        header_match['resultaat'] = table_string(data['match']['totals']['resultaat'])

        header_nomatch = {}
        header_nomatch['id'] = 'payrollnr_nomatch'
        header_nomatch['userHash'] = 'todo USERHASH'
        header_nomatch['img'] = '../static/figs/TODO.png'
        header_nomatch['name'] = 'Niet begroot wel kosten'
        header_nomatch['ordernaam'] = 'Niet begroot wel kosten'
        header_nomatch['begroot'] = table_string(data['nomatch']['totals']['salaris_plan'])
        header_nomatch['geboekt'] = table_string(data['nomatch']['totals']['salaris_geboekt'])
        header_nomatch['obligo'] = table_string(data['nomatch']['totals']['salaris_obligo'])
        header_nomatch['resultaat'] = table_string(data['nomatch']['totals']['resultaat'])

        header_nokosten = {}
        header_nokosten['id'] = 'payrollnr_nokosten'
        header_nokosten['userHash'] = 'todo USERHASH'
        header_nokosten['img'] = '../static/figs/TODO.png'
        header_nokosten['name'] = 'Wel begroot geen kosten'
        header_nokosten['ordernaam'] = 'Wel begroot geen kosten'
        header_nokosten['begroot'] = table_string(data['nokosten']['totals']['salaris_plan'])
        header_nokosten['geboekt'] = table_string(data['nokosten']['totals']['salaris_geboekt'])
        header_nokosten['obligo'] = table_string(data['nokosten']['totals']['salaris_obligo'])
        header_nokosten['resultaat'] = table_string(data['nokosten']['totals']['resultaat'])

        tiepe_tables.append(self.webrender.salaris_table_order(table_match_items, header_match, 'persoon'))
        tiepe_tables.append(self.webrender.salaris_table_order(table_nomatch_items, header_nomatch, 'persoon'))
        tiepe_tables.append(self.webrender.salaris_table_order(table_nokosten_items, header_nokosten, 'persoon'))

        return tiepe_tables
    def render_order_tables(self, data):
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
            for payrollnr in data['orders'][order]['payrollnrs'].keys():
                row = data['orders'][order]['payrollnrs'][payrollnr]
                html = {}
                html['naam'] = row['naam']
                html['personeelsnummer'] = payrollnr  #TODO: on mouseover show all personeelsnummers that are linked to this number
                html['begroot'] = table_string(row['salaris_plan'])
                html['geboekt'] = table_string(row['salaris_geboekt'])
                html['obligo'] = table_string(row['salaris_obligo'])
                html['resultaat'] = table_string(row['resultaat'])
                html['resultaat_perc'] = '%.f' % (row['resultaat_perc']*100) + '%'
                html['td_class'] = 'success' if row['match'] else 'danger'
                table_items.append(self.webrender.salaris_personeel_regel(html))

            order_tables.append(self.webrender.salaris_table_order(table_items, header, 'order'))

        return order_tables

    def render_settings(self):
        # TODO add settings form
        form_settings = 'todo form met optie'
        return self.webrender.salaris_settings(form_settings)


    def render_summary(self, data):
        begroot = data['totals']['salaris_plan']
        geboekt =  data['totals']['salaris_geboekt']
        obligo = data['totals']['salaris_obligo']
        kosten = data['totals']['salaris_geboekt'] + data['totals']['salaris_obligo']
        resultaat = data['totals']['resultaat']

        html = {}
        html['begroot'] = table_string(begroot)
        html['geboekt'] = table_string(geboekt)
        html['obligo'] = table_string(obligo)
        html['resultaat'] = table_string(resultaat)
        html['totaalkosten'] = table_string(kosten)

        return self.webrender.salaris_summary(html)

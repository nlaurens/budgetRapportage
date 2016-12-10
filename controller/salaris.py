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
        self.ordergroup_file = str(web.input(ordergroup='LION')['ordergroup'])
        self.ordergroup = model.ordergroup.load(self.ordergroup_file)
        self.orders = self.ordergroup.list_orders_recursive().keys()
        if str(web.input(subgroup='')['subgroup']) != '':
            self.subordergroup = self.ordergroup.find(str(web.input(subgroup='')['subgroup']))
            self.orders = self.subordergroup.list_orders_recursive().keys()

        # Forms
        dropdown_options = self.dropdown_options()
        self.form_settings_simple = form.Form(
                form.Dropdown('ordergroup', dropdown_options['ordergroups_all'], 
                            description='Order Group', value=self.ordergroup_file),
                form.Button('submit', value='salaris_settings')
        )


    def process_sub(self):
        regels = model.regels.load(table_names_load=['salaris_plan', 'salaris_geboekt', 'salaris_obligo'],orders_load=self.orders)
        data = self.create_data_structure(regels)

        report = {}
        report['settings'] = self.render_settings()
        report['summary'] = self.render_summary(data)
        report['body'] = self.render_body(data)
        report['javaScripts'] = self.webrender.salaris_javascripts(data['orders'].keys() + ['payrollnr_nomatch', 'payrollnr_nokosten','payrollnr_match'])

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
        try:  # not always are there obligo's around
            obligo = regels.split(['tiepe', 'personeelsnummer'])['salaris_obligo'] 
        except:
            obligo = None

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
                    data['payrollnrs'][payrollnr] = {'naam':regel.personeelsnaam, 'match':match, 'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0, 'orders':{}}

                data['payrollnrs'][payrollnr]['match'] = match or data['payrollnrs'][payrollnr]['match']  # once it is true it should stay true
                data['payrollnrs'][payrollnr][regel.tiepe] += regel.kosten
                data['payrollnrs'][payrollnr]['resultaat'] = data['payrollnrs'][payrollnr]['salaris_plan'] - data['payrollnrs'][payrollnr]['salaris_geboekt'] - data['payrollnrs'][payrollnr]['salaris_obligo']
                if data['payrollnrs'][payrollnr]['salaris_plan'] > 0:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = data['payrollnrs'][payrollnr]['salaris_geboekt'] / data['payrollnrs'][payrollnr]['salaris_plan']
                else:
                    data['payrollnrs'][payrollnr]['resultaat_perc'] = 0

                if order not in data['payrollnrs'][payrollnr]['orders']:
                    data['payrollnrs'][payrollnr]['orders'][order] = {'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}

                data['payrollnrs'][payrollnr]['orders'][order][regel.tiepe] += regel.kosten
                data['payrollnrs'][payrollnr]['orders'][order]['resultaat'] = data['payrollnrs'][payrollnr]['orders'][order]['salaris_plan'] - data['payrollnrs'][payrollnr]['orders'][order]['salaris_obligo'] - data['payrollnrs'][payrollnr]['orders'][order]['salaris_geboekt']

        # data - match/nomatch/nokosten - ..
        # We have to this this in sep. loop because we need the
        # plan/geboekt/obligo regels matched first.
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
        payroll_map = {}  # { 'persnr': payrollnummer }
        if regels_obligo:
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
        tiepe_tables = self.render_tiepe_tables(data)

        return self.webrender.salaris_body(order_tables, tiepe_tables)


    def render_tiepe_tables(self, data):
        tiepe_tables = []
        headers = {}
        headers['names'] = { 'match':'Begroot en kosten', 'nomatch':'Niet begroot wel kosten', 'nokosten':'Wel begroot geen kosten'}

        for tiepe in ['match', 'nomatch', 'nokosten']:
            table = []

            headers[tiepe] = {}
            headers[tiepe]['id'] = 'payrollnr_' + tiepe
            headers[tiepe]['userHash'] = 'todo USERHASH'
            headers[tiepe]['img'] = '../static/figs/TODO.png'
            headers[tiepe]['name'] = headers['names'][tiepe]
            headers[tiepe]['ordernaam'] = headers['names'][tiepe]
            headers[tiepe]['begroot'] = table_string(data[tiepe]['totals']['salaris_plan'])
            headers[tiepe]['geboekt'] = table_string(data[tiepe]['totals']['salaris_geboekt'])
            headers[tiepe]['obligo'] = table_string(data[tiepe]['totals']['salaris_obligo'])
            headers[tiepe]['resultaat'] = table_string(data[tiepe]['totals']['resultaat'])

            for payrollnr in data[tiepe]['payrollnrs'].keys():
                item = data[tiepe]['payrollnrs'][payrollnr]
                row = {}
                row['naam'] = item['naam']
                row['personeelsnummer'] = payrollnr  #TODO: on mouseover show all personeelsnummers that are linked to this number
                row['begroot'] = table_string(item['salaris_plan'])
                row['geboekt'] = table_string(item['salaris_geboekt'])
                row['obligo'] = table_string(item['salaris_obligo'])
                row['resultaat'] = table_string(item['resultaat'])
                row['resultaat_perc'] = '%.f' % (item['resultaat_perc']*100) + '%'
                row['td_class'] = 'success' if item['match'] else 'danger'
                row['details'] = False
                row['orders'] = [] 
                for order in item['orders']:
                    row['details'] = True
                    order_item = {'ordernummer':'%s - %s' % (data['orders'][order]['naam'], order) }
                    for key in ['salaris_plan', 'salaris_obligo', 'salaris_geboekt', 'resultaat']:
                        order_item[key] = table_string(item['orders'][order][key])
                    row['orders'].append(order_item)

                table.append(self.webrender.salaris_personeel_regel(row))

            tiepe_tables.append(self.webrender.salaris_table_order(table, headers[tiepe], 'persoon'))

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
                item = data['orders'][order]['payrollnrs'][payrollnr]
                row = {}
                row['naam'] = item['naam']
                row['personeelsnummer'] = payrollnr  #TODO: on mouseover show all personeelsnummers that are linked to this number
                row['begroot'] = table_string(item['salaris_plan'])
                row['geboekt'] = table_string(item['salaris_geboekt'])
                row['obligo'] = table_string(item['salaris_obligo'])
                row['resultaat'] = table_string(item['resultaat'])
                row['resultaat_perc'] = '%.f' % (item['resultaat_perc']*100) + '%'
                row['td_class'] = 'success' if item['match'] else 'danger'
                row['details'] = False  
                table_items.append(self.webrender.salaris_personeel_regel(row))

            order_tables.append(self.webrender.salaris_table_order(table_items, header, 'order'))

        return order_tables

    def render_settings(self):
        form_settings = self.form_settings_simple
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

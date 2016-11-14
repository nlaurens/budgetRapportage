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
        #data = self.format_data(data)
        #body = self.render_body(data)
        report = {}
        report['settings'] = self.render_settings()
        report['summary'] = self.render_summary(data)
        report['body'] = self.render_body(data)
        report['javaScripts'] = self.java_scripts(regels)

        self.body = self.webrender.salaris(report)
        return
        
        ######################################
        #OLD
        ######################################
        regels_per_tiepe = regels.split(['tiepe'])
        matchpersoneelsnummers, no_match_per_order = self.correlate_personeelsnummers(regels_per_tiepe)
        print matchpersoneelsnummers
        print no_match_per_order
        body, totals = self.table_html(regels_per_tiepe, matchpersoneelsnummers, no_match_per_order)

        report = {}
        report['settings'] = self.render_settings()
        report['summary'] = self.get_summary(totals)
        report['body'] = body
        report['javaScripts'] = self.java_scripts(regels_per_tiepe)

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

      data['orders'][<ordernummer>][<payrollnr>] = {'match' as Boolean (True if begroot and realisatie/obligo on the correct order),
                                                    'begroot/realisatie/obligo/resultaat' as decimal, 
                                                     'naam' as string, 'realiatie-perc' as decimal}

    """
    def create_data_structure(self, regels):
        data = { 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}, 'orders':{}, 'payrollnrs':{} }  

        obligo = regels.split(['tiepe', 'personeelsnummer'])['salaris_obligo'] 
        payroll_map = self.payroll_map(obligo)

        regels_per_order = regels.split(['ordernummer'])
        payrollnr_new = 0  # used for unkown payroll <-> persnrs
        for order, regelList in regels_per_order.iteritems():
            if order not in data['orders']:
                data['orders'][order] = { 'naam':'TODO NAAM ORDER', 'totals':{'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0} }  

            for regel in regelList.regels:
                match = False
                if regel.tiepe == 'salaris_geboekt' or regel.tiepe == 'salaris_plan':  
                    if regel.personeelsnummer in payroll_map:
                        payrollnr = payroll_map[regel.personeelsnummer]
                        match = True
                    else:
                        payrollnr = payrollnr_new + 1
                else:
                    payrollnr = regel.payrollnummer

                # data - order - payroll
                if payrollnr not in data['orders'][order]:
                    data['orders'][order][payrollnr] = {'naam':regel.personeelsnaam, 'match':match, 'salaris_plan':0, 'salaris_obligo':0, 'salaris_geboekt':0, 'resultaat':0}
                data['orders'][order][payrollnr]['match'] = match or data['orders'][order][payrollnr]['match']  # once it is true it should stay true
                data['orders'][order][payrollnr][regel.tiepe] += regel.kosten
                data['orders'][order][payrollnr]['resultaat'] = data['orders'][order][payrollnr]['salaris_plan'] - data['orders'][order][payrollnr]['salaris_geboekt'] - data['orders'][order][payrollnr]['salaris_obligo']
                if data['orders'][order][payrollnr]['salaris_plan'] > 0:
                    data['orders'][order][payrollnr]['resultaat_perc'] = data['orders'][order][payrollnr]['salaris_geboekt'] / data['orders'][order][payrollnr]['salaris_plan']
                else:
                    data['orders'][order][payrollnr]['resultaat_perc'] = 0

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


    def correlate_personeelsnummers(self, regels_per_tiepe):
        # Cross personeelsnummers begroting -> boekingsnummers
        begroot = regels_per_tiepe['salaris_plan'].split(['personeelsnummer'])
        kosten = regels_per_tiepe['salaris_geboekt'].split(['personeelsnummer'])
        obligo = regels_per_tiepe['salaris_obligo'].split(['personeelsnummer'])

        matchpersoneelsnummers = {} # personeelsnummer in kosten: { regels begroot}
        no_match_per_order = {} # order : {regelList met regels}
        for begrootpersoneelsnummer, begroot_regels_list in begroot.iteritems():

            matchfound = False
            if begrootpersoneelsnummer:
                #convert 2xx -> 9xxx, 1xxx -> 8xxxx
                if 10000000 <= begrootpersoneelsnummer < 20000000:
                    begrootpersoneelsnummer += 70000000
                elif 20000000 <= begrootpersoneelsnummer < 30000000:
                    begrootpersoneelsnummer += 70000000

                if begrootpersoneelsnummer in kosten.keys():
                    matchpersoneelsnummers[begrootpersoneelsnummer] = begroot_regels_list
                    matchfound = True

            if not matchfound or not begrootpersoneelsnummer:
                begroot_regels_dict_per_order = begroot_regels_list.split(['ordernummer'])
                for order, begroot_regels_list in begroot_regels_dict_per_order.iteritems():
                    if order not in no_match_per_order:
                        no_match_per_order[order] = begroot_regels_list
                    else:
                        no_match_per_order[order].extend(begroot_regels_list)

        return matchpersoneelsnummers, no_match_per_order


    def table_html(self, regels_per_tiepe, matchpersoneelsnummers, no_match_per_order):
        # Parse all orders & begrote kosten:
        obligo_dict = {} #regels_per_tiepe['salaris_plan'].split(['ordernummer'])  # TODO use real obligo here
        kosten_dict = regels_per_tiepe['salaris_geboekt'].split(['ordernummer', 'personeelsnummer'])

        total = {}
        total['begroot'] = 0
        total['geboekt'] = 0
        total['obligo'] = 0
        parsed_orders = []
        for order in kosten_dict.keys():
            #TODO dis-en-tangle html and analysis
            html_order, total_order = self.parse_order(order, kosten_dict, obligo_dict, matchpersoneelsnummers, no_match_per_order)
            total['begroot'] += total_order['begroot']
            total['geboekt'] += total_order['geboekt']
            total['obligo'] += total_order['obligo']
            parsed_orders.append(html_order)

        # Begroot maar geen kosten
        empty_orders = []
        for order, regelList in no_match_per_order.iteritems():
            html_order, total_order_begroot = self.parse_empty_order(order, regelList)
            total['begroot'] += total_order_begroot
            empty_orders.append(html_order)

        return self.webrender.salaris_body(parsed_orders, empty_orders), total


    def parse_order(self, order, kosten_dict, obligo_dict, matchpersoneelsnummers, no_match_per_order):
        order_rows = []
        begroot = 0
        total_order = {}
        total_order['geboekt'] = 0
        total_order['begroot'] = 0
        total_order['resultaat'] = 0
        total_order['obligo'] = 0

        #Geboekte kosten + eventueel begroting
        for personeelsnummer, regelsGeboekt in kosten_dict[order].iteritems():
            ordernaam = regelsGeboekt.regels[0].ordernaam
            naam_geboekt = regelsGeboekt.regels[0].personeelsnaam
            geboekt = regelsGeboekt.total()

            naam_begroot = '' # Reset begroot to not found
            begroot = 0
            if personeelsnummer in matchpersoneelsnummers:
                persoonbegroot = matchpersoneelsnummers[personeelsnummer].split(['ordernummer'])
                if order in persoonbegroot:
                    begroot = persoonbegroot[order].total()
                    naam_begroot = persoonbegroot[order].regels[0].personeelsnaam
            row = {}
            row['personeelsnummer'] = personeelsnummer
            row['naam'] = naam_geboekt
            row['resultaat_perc'] = 0
            row['begroot'] = begroot
            row['geboekt'] = geboekt
            row['resultaat'] = begroot - geboekt
            row['td_class'] = 'danger'
            if naam_begroot != '' and begroot > 0:
                row['naam'] = naam_begroot
                row['resultaat_perc'] = (row['geboekt'] / begroot) * 100
                row['td_class'] = 'success'

            total_order['geboekt'] +=  row['geboekt']
            total_order['begroot'] +=  row['begroot']
            total_order['resultaat'] += row['resultaat']
            order_rows.append(self.personeel_regel_to_html(row))

        # Begrote personen zonder daadwerkelijke kosten
        if order in no_match_per_order:
            for regel in no_match_per_order[order].regels:
                total_order['begroot'] += regel.kosten
                row = {}
                row['personeelsnummer'] = regel.personeelsnummer
                row['naam'] = regel.personeelsnaam
                row['begroot'] = regel.kosten
                row['geboekt'] = 0
                row['resultaat'] = regel.kosten
                row['resultaat_perc'] = 0
                row['td_class'] = 'danger'
                order_rows.append(self.personeel_regel_to_html(row))
            del no_match_per_order[order] #Remove so we end up with a list of remaining begrotingsposten

        #Obligos
        if order in obligo_dict:
            for regel in obligo_dict[order].regels:
                if regel.kosten > 0:
                    row = {}
                    row['personeelsnummer'] = 'Obligos'
    #TODO omschrijving obligo invullen
                    row['naam'] = 'TODO'
                    row['begroot'] = 0
                    row['geboekt'] = regel.kosten
                    row['resultaat'] = - regel.kosten
                    row['resultaat_perc'] = 0
                    row['td_class'] = ''
                    order_rows.append(self.personeel_regel_to_html(row))
                    total_order['obligo'] += regel.kosten

        header = {}
        header['id'] = order
        header['userHash'] = 'todo USERHASH'
        header['img'] = '../static/figs/TODO.png'
        header['name'] = ordernaam + ' - ' + str(order)
        header['ordernaam'] = ordernaam
        header['begroot'] = table_string(total_order['begroot'])
        header['geboekt'] = table_string(total_order['geboekt'])
        header['obligo'] = table_string(total_order['obligo'])
        header['resultaat'] = table_string(total_order['resultaat'])
        html_table = self.webrender.salaris_table_order(order_rows, header)
        return html_table, total_order


    def personeel_regel_to_html(self, row):
        html = row.copy()
        html['personeelsnummer'] = row['personeelsnummer']
        html['name'] = row['naam']
        html['begroot'] = table_string(row['begroot'])
        html['geboekt'] =  table_string(row['geboekt'])
        html['resultaat'] = table_string(row['resultaat'])
        html['resultaat_perc'] = '%.f' % row['resultaat_perc'] + '%'
        html['td_class'] = row['td_class']
        return self.webrender.salaris_personeel_regel(html)


    def parse_empty_order(self, order, regel_list):
        order_rows = []
        total_order_begroot = 0
        for regel in regel_list.regels:
            row = {}
            row['personeelsnummer'] = regel.personeelsnummer
            row['naam'] = regel.personeelsnaam
            row['begroot'] = regel.kosten
            row['geboekt'] = 0
            row['obligo'] = 0
            row['resultaat'] = regel.kosten
            row['resultaat_perc'] = 0
            row['td_class'] = 'danger'
            order_rows.append(self.personeel_regel_to_html(row))
            total_order_begroot += regel.kosten

        header = {}
        header['id'] = order
        header['userHash'] = 'todo UhserHASH'
        header['img'] = '../static/figs/TODO.png'
        header['name'] = order
        header['ordernaam'] = 'todo order naam'
        header['begroot'] = table_string(total_order_begroot)
        header['geboekt'] = table_string(0)
        header['obligo'] = 0
        header['resultaat'] = table_string(-total_order_begroot)
        html_table = self.webrender.salaris_table_order(order_rows, header)
        return html_table, total_order_begroot


    def render_body(self, data):
        return 'TODO'

    def render_settings(self):
        # TODO add settings form
        form_settings = 'todo form met optie'
        return self.webrender.salaris_settings(form_settings)


    def java_scripts(self, data):
        regels_per_tiepe = regels.split(['tiepe'])
        regels_geboekt = regels['salaris_plan']
        regels_begroot = regels['salaris_geboekt']

        orders_geboekt = regels_geboekt.split(['ordernummer']).keys()
        orders_begroot = regels_begroot.split(['ordernummer']).keys()
        orders = set(orders_geboekt + orders_begroot)

        return self.webrender.salaris_javascripts(orders)


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

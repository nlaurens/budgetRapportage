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
        regels = model.regels.load(table_names_load=['salaris_plan', 'salaris_geboekt'],orders_load=self.orders)
        regels_per_tiepe = regels.split(['tiepe'])

        matchpersoneelsnummers, no_match_per_order = self.correlate_personeelsnummers(regels_per_tiepe)
        body, totals = self.table_html(regels_per_tiepe, matchpersoneelsnummers, no_match_per_order)

        report = {}
        report['settings'] = self.render_settings()
        report['summary'] = self.get_summary(totals)
        report['body'] = body
        report['javaScripts'] = self.java_scripts(regels_per_tiepe)

        self.body = self.webrender.salaris(report)


    def correlate_personeelsnummers(self, regels_per_tiepe):
        # Cross personeelsnummers begroting -> boekingsnummers
        begroot = regels_per_tiepe['salaris_plan'].split(['personeelsnummer'])
        kosten = regels_per_tiepe['salaris_geboekt'].split(['personeelsnummer'])

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
        obligo_dict = regels_per_tiepe['salaris_plan'].split(['ordernummer'])
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


    def render_settings(self):
        # TODO add settings form
        form_settings = 'todo form met optie'
        return self.webrender.salaris_settings(form_settings)


    def java_scripts(self, regels):
        regels_geboekt = regels['salaris_plan']
        regels_begroot = regels['salaris_geboekt']

        orders_geboekt = regels_geboekt.split(['ordernummer']).keys()
        orders_begroot = regels_begroot.split(['ordernummer']).keys()
        orders = set(orders_geboekt + orders_begroot)

        return self.webrender.salaris_javascripts(orders)


    def get_summary(self, totals):
        kosten = totals['geboekt'] + totals['obligo']
        resultaat = totals['begroot'] - kosten

        html = {}
        html['begroot'] = table_string(totals['begroot'])
        html['geboekt'] = table_string(totals['geboekt'])
        html['obligo'] = table_string(totals['obligo'])
        html['resultaat'] = table_string(resultaat)
        html['totaalkosten'] = table_string(kosten)

        return self.webrender.salaris_summary(html)

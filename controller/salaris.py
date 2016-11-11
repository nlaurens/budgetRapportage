from controller import Controller
import web

import numpy as np


class Salaris(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Salaris'
        self.module = 'salaris'
        self.webrender = web.template.render('webpages/salaris/')

        # Salaris specific:

    def process_sub(self):
        #orders_allowed = orders_in_grootboekgroep(groepstr)
        #regels = get_HR_regels(jaar, orders_allowed)

        #matchpersoneelsnummers, no_match_per_order = correlate_personeelsnummers(regels['salaris_plan'], regels['salaris_geboekt'])

        #body, totals = table_html(render, regels, matchpersoneelsnummers, no_match_per_order)
        #settings = settings_html(render, jaar)
        #java_scripts = java_scripts(render, regels['salaris_geboekt'], regels['salaris_plan'])
        #summary = get_summary(render, totals)

        settings = 'settings' 
        summary = ' summary' 
        body = 'body'
        java_scripts = 'java_scripts'

        report = {}
        report['settings'] = settings
        report['summary'] = summary
        report['body'] = body
        report['javaScripts'] = java_scripts

        self.body = self.webrender.salaris(report)

def table_string(value):
    value /= 1000
    if value == 0 or np.abs(value) < 0.5:
        return '&nbsp;'
    else:
        return '%.f' % value


def personeel_regel_to_html(row, render):
    html = row.copy()
    html['personeelsnummer'] = row['personeelsnummer']
    html['name'] = row['naam']
    html['begroot'] = table_string(row['begroot'])
    html['geboekt'] =  table_string(row['geboekt'])
    html['resultaat'] = table_string(row['resultaat'])
    html['resultaat_perc'] = '%.f' % row['resultaat_perc'] + '%'
    html['td_class'] = row['td_class']
    return render.salaris_personeel_regel(html)


def parse_order(render, order, kosten_dict, obligo_dict, matchpersoneelsnummers, no_match_per_order):
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
            persoonbegroot = matchpersoneelsnummers[personeelsnummer].split_by_regel_attributes(['ordernummer'])
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
        order_rows.append(personeel_regel_to_html(row, render))

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
            order_rows.append(personeel_regel_to_html(row, render))
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
                order_rows.append(personeel_regel_to_html(row, render))
                total_order['obligo'] += regel.kosten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = '../static/figs/TODO.png'
    header['name'] = ordernaam + ' - ' + str(order)
    header['ordernaam'] = ordernaam
    header['begroot'] = table_string(total_order['begroot'])
    header['geboekt'] = table_string(total_order['geboekt'])
    header['obligo'] = table_string(total_order['obligo'])
    header['resultaat'] = table_string(total_order['resultaat'])
    html_table = render.salaris_table_order(order_rows, header)
    return html_table, total_order


def parse_empty_order(render, order, regel_list):
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
        order_rows.append(personeel_regel_to_html(row, render))
        total_order_begroot += regel.kosten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = '../static/figs/TODO.png'
    header['name'] = order
    header['ordernaam'] = 'todo order naam'
    header['begroot'] = table_string(total_order_begroot)
    header['geboekt'] = table_string(0)
    header['obligo'] = 0
    header['resultaat'] = table_string(-total_order_begroot)
    html_table = render.salaris_table_order(order_rows, header)
    return html_table, total_order_begroot


def table_html(render, regels, matchpersoneelsnummers, no_match_per_order):
    # Parse all orders & begrote kosten:
    kosten_dict = regels['salaris_geboekt'].split_by_regel_attributes(['ordernummer', 'personeelsnummer'])
    obligo_dict = regels['salaris_plan'].split_by_regel_attributes(['ordernummer'])
    total = {}
    total['begroot'] = 0
    total['geboekt'] = 0
    total['obligo'] = 0
    parsed_orders = []
    for order in kosten_dict.keys():
        html_order, total_order = parse_order(render, order, kosten_dict, obligo_dict, matchpersoneelsnummers, no_match_per_order)
        total['begroot'] += total_order['begroot']
        total['geboekt'] += total_order['geboekt']
        total['obligo'] += total_order['obligo']
        parsed_orders.append(html_order)

    # Begroot maar geen kosten
    empty_orders = []
    for order, regelList in no_match_per_order.iteritems():
        html_order, total_order_begroot = parse_empty_order(render, order, regelList)
        total['begroot'] += total_order_begroot
        empty_orders.append(html_order)

    return render.salaris_body(parsed_orders, empty_orders), total

def settings_html(render, jaar):
    form_settings = 'todo form met optie'
    lastupdate = model.regels.last_update()
    return render.salaris_settings(lastupdate, form_settings)

def java_scripts(render, regels_geboekt, regels_begroot):
    orders_geboekt = regels_geboekt.split_by_regel_attributes(['ordernummer']).keys()
    orders_begroot = regels_begroot.split_by_regel_attributes(['ordernummer']).keys()
    orders = set(orders_geboekt + orders_begroot)

    return render.salaris_javascripts(orders)


def get_summary(render,totals):
    kosten = totals['geboekt'] + totals['obligo']
    resultaat = totals['begroot'] - kosten

    html = {}
    html['begroot'] = table_string(totals['begroot'])
    html['geboekt'] = table_string(totals['geboekt'])
    html['obligo'] = table_string(totals['obligo'])
    html['resultaat'] = table_string(resultaat)
    html['totaalkosten'] = table_string(kosten)

    return render.salaris_summary(html)




def orders_in_grootboekgroep(groepstr):
#TODO in variable voor andere ordergroepen
    if groepstr != '':
        root = rootOrderGroep.load('LION')
        root = root.find(groepstr)
    else:
        root = OrderGroep.load('LION')

    orders_allowed = root.list_orders_recursive()

    return orders_allowed

def get_HR_regels(jaar, orders):
#TODO selecteren op jaar. maar db heeft nu nog geen jaar. moet tijdens importeren aangepast worden.
    table_names = ['salaris_geboekt', 'salaris_plan', 'salaris_plan']
    regels = model.get_regellist_per_table(table_names, orders=orders)

    return regels

def correlate_personeelsnummers(regels_begroot, regels_geboekt):
# Cross personeelsnummers begroting -> boekingsnummers
    begroot = regels_begroot.split_by_regel_attributes(['personeelsnummer'])
    kosten = regels_geboekt.split_by_regel_attributes(['personeelsnummer'])

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
            begroot_regels_dict_per_order = begroot_regels_list.split_by_regel_attributes(['ordernummer'])
            for order, begroot_regels_list in begroot_regels_dict_per_order.iteritems():
                if order not in no_match_per_order:
                    no_match_per_order[order] = begroot_regels_list
                else:
                    no_match_per_order[order].extend(begroot_regels_list)

    return matchpersoneelsnummers, no_match_per_order


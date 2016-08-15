from controller import Controller
import web
from web import form
import model.db
import budget

import numpy as np

class Salaris(Controller):
    def __init__(self):
        Controller.__init__(self)

        #subclass specific
        self.title = 'Salaris'
        self.module = 'salaris'
        self.webrender = web.template.render('webpages/salaris/')

        #Salaris specific:


    def process_sub(self):
        self.body = 'dummy salaris'
        return #dummy stop
        #OLD
        salaris = websalaris.groep_report(userHash, render, groep, jaar)
        self.body = self.webrender.salaris(salaris)

def table_string(value):
    value = value/1000
    if value == 0 or np.abs(value) < 0.5:
        return '&nbsp;'
    else:
        return ('%.f' % value)


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


def parse_order(render, order, kostenDict, obligoDict, matchpersoneelsnummers, noMatchPerOrder):
    orderRows = []
    begroot = 0
    totalOrder = {}
    totalOrder['geboekt'] = 0
    totalOrder['begroot'] = 0
    totalOrder['resultaat'] = 0
    totalOrder['obligo'] = 0


    #Geboekte kosten + eventueel begroting
    for personeelsnummer, regelsGeboekt in kostenDict[order].iteritems():
        ordernaam = regelsGeboekt.regels[0].ordernaam
        naamGeboekt = regelsGeboekt.regels[0].personeelsnaam
        geboekt = regelsGeboekt.total()

        naamBegroot = '' # Reset begroot to not found
        begroot = 0
        if personeelsnummer in matchpersoneelsnummers:
            persoonbegroot = matchpersoneelsnummers[personeelsnummer].split_by_regel_attributes(['ordernummer'])
            if order in persoonbegroot:
                begroot = persoonbegroot[order].total()
                naamBegroot = persoonbegroot[order].regels[0].personeelsnaam
        row = {}
        row['personeelsnummer'] = personeelsnummer
        row['naam'] = naamGeboekt
        row['resultaat_perc'] = 0
        row['begroot'] = begroot
        row['geboekt'] = geboekt
        row['resultaat'] = begroot - geboekt
        row['td_class'] = 'danger'
        if naamBegroot != '' and begroot > 0:
            row['naam'] = naamBegroot
            row['resultaat_perc'] = (row['geboekt'] / begroot) * 100
            row['td_class'] = 'success'

        totalOrder['geboekt'] +=  row['geboekt']
        totalOrder['begroot'] +=  row['begroot']
        totalOrder['resultaat'] += row['resultaat']
        orderRows.append(personeel_regel_to_html(row, render))

    # Begrote personen zonder daadwerkelijke kosten
    if order in noMatchPerOrder:
        for regel in noMatchPerOrder[order].regels:
            totalOrder['begroot'] += regel.kosten
            row = {}
            row['personeelsnummer'] = regel.personeelsnummer
            row['naam'] = regel.personeelsnaam
            row['begroot'] = regel.kosten
            row['geboekt'] = 0
            row['resultaat'] = regel.kosten
            row['resultaat_perc'] = 0
            row['td_class'] = 'danger'
            orderRows.append(personeel_regel_to_html(row, render))
        del noMatchPerOrder[order] #Remove so we end up with a list of remaining begrotingsposten

    #Obligos
    if order in obligoDict:
        for regel in obligoDict[order].regels:
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
                orderRows.append(personeel_regel_to_html(row, render))
                totalOrder['obligo'] += regel.kosten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = '../static/figs/TODO.png'
    header['name'] = ordernaam + ' - ' + str(order)
    header['ordernaam'] = ordernaam
    header['begroot'] = table_string(totalOrder['begroot'])
    header['geboekt'] = table_string(totalOrder['geboekt'])
    header['obligo'] = table_string(totalOrder['obligo'])
    header['resultaat'] = table_string(totalOrder['resultaat'])
    html_table = render.salaris_table_order(orderRows, header)
    return html_table, totalOrder


def parse_empty_order(render, order, regelList):
    orderRows = []
    totalOrderBegroot = 0
    for regel in regelList.regels:
        row = {}
        row['personeelsnummer'] = regel.personeelsnummer
        row['naam'] = regel.personeelsnaam
        row['begroot'] = regel.kosten
        row['geboekt'] = 0
        row['obligo'] = 0
        row['resultaat'] = regel.kosten
        row['resultaat_perc'] = 0
        row['td_class'] = 'danger'
        orderRows.append(personeel_regel_to_html(row, render))
        totalOrderBegroot += regel.kosten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = '../static/figs/TODO.png'
    header['name'] = order
    header['ordernaam'] = 'todo order naam'
    header['begroot'] = table_string(totalOrderBegroot)
    header['geboekt'] = table_string(0)
    header['obligo'] = 0
    header['resultaat'] = table_string(-totalOrderBegroot)
    html_table = render.salaris_table_order(orderRows, header)
    return html_table, totalOrderBegroot


def table_html(render, regels, matchpersoneelsnummers, noMatchPerOrder):
    # Parse all orders & begrote kosten:
    kostenDict = regels['salaris_geboekt'].split_by_regel_attributes(['ordernummer', 'personeelsnummer'])
    obligoDict = regels['salaris_plan'].split_by_regel_attributes(['ordernummer'])
    total = {}
    total['begroot'] = 0
    total['geboekt'] = 0
    total['obligo'] = 0
    parsed_orders = []
    for order in kostenDict.keys():
        html_order, totalOrder = parse_order(render, order, kostenDict, obligoDict, matchpersoneelsnummers, noMatchPerOrder)
        total['begroot'] += totalOrder['begroot']
        total['geboekt'] += totalOrder['geboekt']
        total['obligo'] += totalOrder['obligo']
        parsed_orders.append(html_order)

    # Begroot maar geen kosten
    empty_orders = []
    for order, regelList in noMatchPerOrder.iteritems():
        html_order, totalOrderBegroot = parse_empty_order(render, order, regelList)
        total['begroot'] += totalOrderBegroot
        empty_orders.append(html_order)

    return render.salaris_body(parsed_orders, empty_orders), total

def settings_html(render, jaar):
    form = 'todo form met optie'
    lastupdate = model.last_update()
    return render.salaris_settings(lastupdate, form)

def java_scripts(render, regelsGeboekt, regelsBegroot):
    ordersGeboekt = regelsGeboekt.split_by_regel_attributes(['ordernummer']).keys()
    ordersBegroot = regelsBegroot.split_by_regel_attributes(['ordernummer']).keys()
    orders = set(ordersGeboekt + ordersBegroot)

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


def groep_report(userID, render, groepstr, jaar):
    global userHash
    userHash = userID

    orders_allowed = orders_in_grootboekgroep(groepstr)
    regels = get_HR_regels(jaar, orders_allowed)

    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regels['salaris_plan'], regels['salaris_geboekt'])

    body, totals = table_html(render, regels, matchpersoneelsnummers, noMatchPerOrder)
    settings = settings_html(render, jaar)
    javaScripts = java_scripts(render, regels['salaris_geboekt'], regels['salaris_plan'])
    summary = get_summary(render, totals)

    report = {}
    report['settings'] = settings
    report['summary'] = summary
    report['body'] = body
    report['javaScripts'] = javaScripts
    return report


def orders_in_grootboekgroep(groepstr):
#TODO in variable voor andere ordergroepen
    if groepstr != '':
        root = OrderGroep.load('LION')
        root = root.find(groepstr)
    else:
        root = OrderGroep.load('LION')

    orders_allowed = root.list_orders_recursive()

    return orders_allowed

def get_HR_regels(jaar, orders):
#TODO selecteren op jaar. maar db heeft nu nog geen jaar. moet tijdens importeren aangepast worden.
    tableNames = ['salaris_geboekt', 'salaris_plan', 'salaris_plan']
    regels = model.get_regellist_per_table(tableNames, orders=orders)

    return regels

def correlate_personeelsnummers(regelsBegroot, regelsGeboekt):
# Cross personeelsnummers begroting -> boekingsnummers
    begroot = regelsBegroot.split_by_regel_attributes(['personeelsnummer'])
    kosten = regelsGeboekt.split_by_regel_attributes(['personeelsnummer'])

    matchpersoneelsnummers = {} # personeelsnummer in kosten: { regels begroot}
    noMatchPerOrder = {} # order : {regelList met regels}
    for begrootpersoneelsnummer, begrootRegelsList in begroot.iteritems():

        matchfound = False
        if begrootpersoneelsnummer:
            #convert 2xx -> 9xxx, 1xxx -> 8xxxx
            if (10000000 <= begrootpersoneelsnummer < 20000000):
                begrootpersoneelsnummer = begrootpersoneelsnummer + 70000000
            elif (20000000 <= begrootpersoneelsnummer < 30000000):
                begrootpersoneelsnummer = begrootpersoneelsnummer + 70000000

            if begrootpersoneelsnummer in kosten.keys():
                matchpersoneelsnummers[begrootpersoneelsnummer] = begrootRegelsList
                matchfound = True

        if not matchfound or not begrootpersoneelsnummer:
            begrootRegelsDictPerOrder = begrootRegelsList.split_by_regel_attributes(['ordernummer'])
            for order, begrootRegelsList in begrootRegelsDictPerOrder.iteritems():
                if order not in noMatchPerOrder:
                    noMatchPerOrder[order] = begrootRegelsList
                else:
                    noMatchPerOrder[order].extend(begrootRegelsList)

    return matchpersoneelsnummers, noMatchPerOrder


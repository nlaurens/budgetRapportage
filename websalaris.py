"""
TODO
    * Naam order uit andere db halen, salaris geeft korte namen.. (kostensoort groep?)
    * Plaatjes maken/koppelen
    * Summary van alle totalen maken (totalOrderGeboekt, etc opvangen uit html_table)
    * Obligos salarissen ECHT uit systeem halen (kan! ipv de HR-obligos per order!)
"""
import web
from config import config
import OrderGroep
import GrootBoek
import model
import numpy as np
from RegelList import RegelList


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
            persoonbegroot = matchpersoneelsnummers[personeelsnummer].split_by_regel_attributes(['order'])
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
                row['naam'] = regel.omschrijving
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


def table_html(render, HRregels, matchpersoneelsnummers, noMatchPerOrder):
    # Parse all orders & begrote kosten:
    kostenDict = HRregels['geboekt'].split_by_regel_attributes(['order', 'personeelsnummer'])
    obligoDict = HRregels['obligos'].split_by_regel_attributes(['order'])
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
    ordersGeboekt = regelsGeboekt.split_by_regel_attributes(['order']).keys()
    ordersBegroot = regelsBegroot.split_by_regel_attributes(['order']).keys()
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
    HRregels = get_HR_regels(jaar, orders_allowed)

    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(HRregels['begroot'], HRregels['geboekt'])

    body, totals = table_html(render, HRregels, matchpersoneelsnummers, noMatchPerOrder)
    settings = settings_html(render, jaar)
    javaScripts = java_scripts(render, HRregels['geboekt'], HRregels['begroot'])
    summary = get_summary(render, totals)

    report = {}
    report['settings'] = settings
    report['summary'] = summary
    report['body'] = body
    report['javaScripts'] = javaScripts
    return report


def orders_in_grootboekgroep(groepstr):
    grootboekgroepfile = 'data/grootboekgroep/LION'
    if groepstr != '':
        root = GrootBoekGroep.load(grootboekgroepfile)
        root = root.find(groepstr)
    else:
        root = GrootBoekGroep.load(grootboekgroepfile)

    orders_allowed = root.list_orders_recursive()

    return orders_allowed

def get_HR_regels(jaar, orders):
    HRregels = {}

    regels = model.get_salaris_geboekt_regels(jaar, orders=orders)
    HRregels['geboekt'] = RegelList(regels)

    regels = model.get_salaris_begroot_regels(jaar, orders=orders)
    HRregels['begroot'] = RegelList(regels)

    regels = model.get_obligos_regels(jaar, orders=orders, kostensoorten=[411101])
    HRregels['obligos'] = RegelList(regels)
    return HRregels

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
            begrootRegelsDictPerOrder = begrootRegelsList.split_by_regel_attributes(['order'])
            for order, begrootRegelsList in begrootRegelsDictPerOrder.iteritems():
                if order not in noMatchPerOrder:
                    noMatchPerOrder[order] = begrootRegelsList
                else:
                    noMatchPerOrder[order].extend(begrootRegelsList)

    return matchpersoneelsnummers, noMatchPerOrder

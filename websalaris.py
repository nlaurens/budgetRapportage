"""
TODO
    * Laats geboekte periode kopppelen aan model.regels (nu nog een dummy)
"""
import web
from config import config
import GrootBoekGroep
import GrootBoek
import model
import numpy as np


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
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    html['prognose'] = table_string(row['prognose'])
    html['td_class'] = 'success'
    if row['td_class']:
        html['td_class'] = row['td_class']
    return render.salaris_personeel_regel(html)


def order_regel_to_html(row, render):
    html = row.copy()
#TODO
    html['order'] = row['name']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.report_table_order_regel(html)

def groep_regel_to_html(row, render):
    html = row.copy()
#TODO
    html['name'] = row['name']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.report_table_groep_regel(html)


def parse_orders_in_groep(root, jaar, render, total_groep):
    order_tables = []
    total_groep['name'] = root.descr
    for order, descr in root.orders.iteritems():
        order_table,total_order = parse_order(order, descr, jaar, render)
        order_tables.append(order_table)
        total_groep['begroot'] += total_order['begroot']
        total_groep['realisatie'] += total_order['realisatie']
        total_groep['resultaat'] += total_order['resultaat']

    groep_header = {}
    groep_header['row'] = groep_regel_to_html(total_groep, render)
    groep_header['id'] = root.name
    groep_header['img'] = "../static/figs/"+str(jaar)+"-detailed/1-"+root.name+".png"

    return order_tables, groep_header, total_groep


def parse_groep(root, jaar, render):
    groeptotal = {}
    groeptotal['begroot'] = 0
    groeptotal['realisatie'] = 0
    groeptotal['obligo'] = 0
    groeptotal['resultaat'] = 0
    groeprows = []
    for child in root.children:
        childOrderTables, childheader, childgroep, total = parse_groep(child, jaar, render)
        groeprows.append(render.report_table_groep(childOrderTables, childheader, childgroep))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    order_tables, groepheader, groeptotal = parse_orders_in_groep(root, jaar, render, groeptotal)
    return order_tables, groepheader, groeprows, groeptotal


def fig_html(root, render, jaar):
    figs = ''
    if not root.children:
        graphs = []
        i = 0
        for order, descr in root.orders.iteritems():
            graph = {}
            graph['link'] = ('../view/' + userHash + '/' + str(order))
            graph['png'] = ('../static/figs/'+str(jaar)+'-detailed/1-' + str(order) + '.png')
            #if i%2:
            #    graph['spacer'] = '</tr><tr>'
            #else:
            #    graph['spacer'] = ''
            graph['spacer'] = '</tr><tr>'
            graphs.append(graph)
            i +=1

        figs = render.report_figpage(graphs)
        return figs
    else:
        return None

def parse_order(render, order, kostenDict, matchpersoneelsnummers, noMatchPerOrder, laatstePeriodeGeboekt):
    orderRows = []
    begroot = 0
    totalOrderGeboekt = 0
    totalOrderBegroot = 0
    totalOrderResultaat = 0
    for personeelsnummer, regelsGeboekt in kostenDict[order].iteritems():
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
        if naamBegroot != '':
            row['naam'] = naamBegroot
        row['begroot'] = begroot
        row['realisatie'] = geboekt
        row['prognose'] = (geboekt / laatstePeriodeGeboekt ) * 12
        row['resultaat'] = float(begroot) - row['prognose']
        row['td_class'] = ''
        if begroot == 0:
            row['td_class'] = 'danger'

        totalOrderGeboekt +=  row['realisatie']
        totalOrderBegroot +=  row['begroot']
        totalOrderResultaat += row['resultaat']
        orderRows.append(personeel_regel_to_html(row, render))
    
    if order in noMatchPerOrder:
        for regel in noMatchPerOrder[order].regels:
            totalOrderBegroot += regel.kosten
            row = {}
            row['personeelsnummer'] = regel.personeelsnummer
            row['naam'] = regel.personeelsnaam
            row['begroot'] = regel.kosten
            row['realisatie'] = 0
            row['resultaat'] = regel.kosten
            row['prognose'] = 0
            row['td_class'] = ''
            orderRows.append(personeel_regel_to_html(row, render))
        del noMatchPerOrder[order] #Remove so we end up with a list of remaining begrotingsposten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = 'link to img'
    header['name'] = order
    header['begroot'] = table_string(totalOrderBegroot)
    header['realisatie'] = table_string(totalOrderGeboekt)
    header['resultaat'] = table_string(totalOrderResultaat)
    html_table = render.salaris_table_order(orderRows, header)
    return html_table, totalOrderBegroot, totalOrderGeboekt


def parse_empty_order(render, order, regelList):
    orderRows = []
    totalOrderBegroot = 0
    for regel in regelList.regels:
        row = {}
        row['personeelsnummer'] = regel.personeelsnummer
        row['naam'] = regel.personeelsnaam
        row['begroot'] = regel.kosten
        row['realisatie'] = 0
        row['resultaat'] = regel.kosten
        row['prognose'] = 0
        row['td_class'] = ''
        orderRows.append(personeel_regel_to_html(row, render))
        totalOrderBegroot += regel.kosten

    header = {}
    header['id'] = order
    header['userHash'] = userHash
    header['img'] = 'link to img'
    header['name'] = order
    header['begroot'] = table_string(totalOrderBegroot)
    header['realisatie'] = table_string(0)
    header['resultaat'] = 'TODO'
    html_table = render.salaris_table_order(orderRows, header)
    return html_table, totalOrderBegroot


def table_html(render, regelsGeboekt, regelsBegroot, matchpersoneelsnummers, noMatchPerOrder, laatstePeriodeGeboekt):

    # Parse all orders & begrote kosten:
    kostenDict = regelsGeboekt.split_by_regel_attributes(['order', 'personeelsnummer'])
    totalBegroot = 0
    totalGeboekt = 0
    parsed_orders = []
    i = 0
    for order in kostenDict.keys():
        html_order, totalOrderBegroot, totalOrderGeboekt = parse_order(render, order, kostenDict, matchpersoneelsnummers, noMatchPerOrder, laatstePeriodeGeboekt)
        totalBegroot += totalOrderBegroot
        totalGeboekt += totalOrderGeboekt
        parsed_orders.append(html_order)
        i+=1

    # Begroot maar geen kosten/realisatie:
    empty_orders = []
    for order, regelList in noMatchPerOrder.iteritems():
        html_order, totalOrderBegroot = parse_empty_order(render, order, regelList)
        totalBegroot += totalOrderBegroot
        empty_orders.append(html_order)

    return render.salaris_body(parsed_orders, empty_orders)

def settings_html(render, jaar):
    form = 'FORM met daarin jaar'
    buttons = 'BUTTON'
    lastupdate = '2'
    return render.report_settings(lastupdate, buttons, form)

def java_scripts(render, regelsGeboekt, regelsBegroot):
    ordersGeboekt = regelsGeboekt.split_by_regel_attributes(['order']).keys()
    ordersBegroot = regelsBegroot.split_by_regel_attributes(['order']).keys()
    orders = set(ordersGeboekt + ordersBegroot)

    return render.salaris_javascripts(orders)

def groep_report(userID, render, groepstr, jaar):
    global userHash 
    userHash = userID

    regelsGeboekt, regelsBegroot = get_begroting_geboekt(jaar)
    regelsGeboekt, regelsBegroot = filter_orders_in_groep(regelsGeboekt, regelsBegroot, groepstr)
    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regelsBegroot, regelsGeboekt)
    laatstePeriodeGeboekt = 10 #TODO DUMMY

    body = table_html(render, regelsGeboekt, regelsBegroot, matchpersoneelsnummers, noMatchPerOrder, laatstePeriodeGeboekt)
    settings = settings_html(render, jaar)
    javaScripts = java_scripts(render, regelsGeboekt, regelsBegroot)

    report = {}
    report['settings'] = settings
    report['summary'] = "TODO Summary"
    report['body'] = body
    report['javaScripts'] = javaScripts
    return report


##########################
# NEw webreport:
##########################

from RegelList import RegelList

def filter_orders_in_groep(regelsGeboekt, regelsBegroot, groepstr):
    grootboekgroepfile = 'data/grootboekgroep/LION'
    if groepstr != '':
        root = GrootBoekGroep.load(grootboekgroepfile)
        root = root.find(groepstr)
    else: 
        root = GrootBoekGroep.load(grootboekgroepfile)

    orders_allowed = root.list_orders_recursive()
    regelsGeboekt = regelsGeboekt.filter_regels_by_attribute('order', orders_allowed)
    regelsBegroot = regelsBegroot.filter_regels_by_attribute('order', orders_allowed)

    return regelsGeboekt, regelsBegroot

def get_begroting_geboekt(jaar):
    regels = model.get_salaris_geboekt_regels(jaar)
    regelsGeboekt = RegelList(regels)

    regels = model.get_salaris_begroot_regels(jaar)
    regelsBegroot = RegelList(regels)

    return regelsGeboekt, regelsBegroot

def correlate_personeelsnummers(regelsBegroot, regelsGeboekt):
# Cross personeelsnummers begroting -> boekingsnummers
    begroot = regelsBegroot.split_by_regel_attributes(['personeelsnummer'])
    kosten = regelsGeboekt.split_by_regel_attributes(['personeelsnummer'])

    matchpersoneelsnummers = {} # personeelsnummer in kosten: { regels begroot}
    noMatchPerOrder = {} # order : {regelList met regels}
    for begrootpersoneelsnummer, begrootRegelsList in begroot.iteritems():
        begrootpersoneelsnummer = list(begrootpersoneelsnummer.strip())

        if begrootpersoneelsnummer:
            matchfound = False
            if begrootpersoneelsnummer[0] == '2':
                begrootpersoneelsnummer[0] = '9'
            elif begrootpersoneelsnummer[0] == '1':
                begrootpersoneelsnummer[0] = '8'
            begrootpersoneelsnummer = ''.join(begrootpersoneelsnummer)

            if long(begrootpersoneelsnummer) in kosten.keys():
                matchpersoneelsnummers[long(begrootpersoneelsnummer)] = begrootRegelsList
                matchfound = True

        if not matchfound or not begrootpersoneelsnummer:
            begrootRegelsDictPerOrder = begrootRegelsList.split_by_regel_attributes(['order'])
            for order, begrootRegelsList in begrootRegelsDictPerOrder.iteritems():
                if order not in noMatchPerOrder:
                    noMatchPerOrder[order] = begrootRegelsList
                else:
                    noMatchPerOrder[order].extend(begrootRegelsList)

    return matchpersoneelsnummers, noMatchPerOrder

def cmd_output(userID, groepstr, jaar):
    regelsGeboekt, regelsBegroot = get_begroting_geboekt(jaar)
    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regelsBegroot, regelsGeboekt)

# dict per order per persnr
    kostenDict = regelsGeboekt.split_by_regel_attributes(['order', 'personeelsnummer'])
    totalBegroot = 0
    totalGeboekt = 0
    for order in kostenDict.keys():
        begroot = 0
        totalOrderGeboekt = 0
        totalOrderBegroot = 0
        for personeelsnummer, regelsGeboekt in kostenDict[order].iteritems():
            naamGeboekt = regelsGeboekt.regels[0].personeelsnaam
            geboekt = regelsGeboekt.total()
            totalOrderGeboekt +=  geboekt

            naamBegroot = '' # Reset begroot to not found
            begroot = 0

            if personeelsnummer in matchpersoneelsnummers:
                persoonbegroot = matchpersoneelsnummers[personeelsnummer].split_by_regel_attributes(['order'])
                if order in persoonbegroot:
                    begroot = persoonbegroot[order].total()
                    naamBegroot = persoonbegroot[order].regels[0].personeelsnaam
                    totalOrderBegroot +=  begroot

            print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (order, personeelsnummer, geboekt, begroot, naamGeboekt, naamBegroot)
        
        if order in noMatchPerOrder:
            for regel in noMatchPerOrder[order].regels:
                print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (order, regel.personeelsnummer, 0, regel.kosten, '', regel.personeelsnaam)
                totalOrderBegroot += regel.kosten
            del noMatchPerOrder[order] #Remove so we end up with a list of remaining begrotingsposten

        print 'Total order %s - geboekt %i begroot %i' % (order, totalOrderGeboekt, totalOrderBegroot)
        print ''
        totalBegroot += totalOrderBegroot
        totalGeboekt += totalOrderGeboekt

    print '--------------'
    print 'Begroot maar geen kosten gemaakt op order'
    print ''

    for order, regelList in noMatchPerOrder.iteritems():
        totalOrderBegroot = 0
        for regel in regelList.regels:
            print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (regel.order, regel.personeelsnummer, 0, regel.kosten, '', regel.personeelsnaam)
            totalOrderBegroot += regel.kosten

        totalBegroot += totalOrderBegroot

        print 'Total order %s - geboekt %i begroot %i' % (order, totalOrderGeboekt, totalOrderBegroot)
        print ''

    print 'TOTAL geboekt %i begroot %i' % (totalGeboekt, totalBegroot)

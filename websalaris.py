"""
TODO
    * Change glyph on collapse:
        http://www.bootply.com/73101
    * Collapse/Expand orders

"""
import web
from config import config
import GrootBoekGroep
import GrootBoek
import model
import numpy as np
from RegelList import RegelList

def get_begroting_geboekt(userID, groepstr, jaar):
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
    regelsGeboekt, regelsBegroot = get_begroting_geboekt(userID, groepstr, jaar)
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



#-------------------------
#OLD WEBREPORT:
#-------------------------





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
    return render.salaris_table_personeel_regel(html)


def order_regel_to_html(row, render):
    html = row.copy()
#TODO
    html['order'] = row['name']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.salaris_table_order_regel(html)

def groep_regel_to_html(row, render):
    html = row.copy()
#TODO
    html['name'] = row['name']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.salaris_table_groep_regel(html)


def parse_order(order, descr, jaar, render):
    #parse orders in groep:
    KSgroepen = model.loadKSgroepen()
    grootboek =  [s for s in KSgroepen if "BFRE15E01" in s][0]

    root = GrootBoek.load(order, grootboek, jaar, [])
    root.set_totals()
    html_rows = []
#TODO DUMMY code
    totals_order = {}
    totals_order['begroot'] = 0
    totals_order['realisatie'] = 0
    totals_order['resultaat'] = 0 
    for i in range(0,10):
        begroot = 10000
        realisatie = 20000
        resultaat = -10000
        row = {}
        row['personeelsnummer'] = 'persnNR'
        row['naam'] = 'naam persoon'
        row['begroot'] = begroot
        row['realisatie'] = realisatie
        row['resultaat'] = resultaat
        html_rows.append(personeel_regel_to_html(row, render))

        totals_order['begroot'] += begroot
        totals_order['realisatie'] += realisatie
        totals_order['resultaat'] += resultaat

    order_table = render.salaris_table_order(html_rows)
    return order_table, totals_order

def parse_orders_in_groep(root, jaar, render, total_groep):
    order_tables = []
    total_groep['name'] = root.descr
    print root.descr
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
        groeprows.append(render.salaris_table_groep(childOrderTables, childheader, childgroep))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    order_tables, groepheader, groeptotal = parse_orders_in_groep(root, jaar, render, groeptotal)
    return order_tables, groepheader, groeprows, groeptotal


def table_html(root, render, jaar):
    table = []
    childtable = []
    groeptotal = {}
    groeptotal['begroot'] = 0
    groeptotal['realisatie'] = 0
    groeptotal['obligo'] = 0
    groeptotal['resultaat'] = 0
    for child in root.children:
        rows, header, groeprows, total = parse_groep(child, jaar, render)
        childtable.append(render.salaris_table_groep(rows, header, groeprows))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    #add orders of the top group (if any)
    order_tables, header,total = parse_orders_in_groep(root, jaar, render, groeptotal)
    table.append(render.salaris_table_groep(order_tables, header, childtable))

    body = render.salaris_table(table)
    return body

def settings_html(root, render, jaar):
    form = 'FORM met daarin jaar'
    buttons = 'BUTTON'
    lastupdate = '2'
    return render.salaris_settings(lastupdate, buttons, form)

def groep_report(userID, render, groepstr, jaar):
#NEW websalaris
    report = {}
    regelsGeboekt, regelsBegroot = get_begroting_geboekt(userID, groepstr, jaar)
    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regelsBegroot, regelsGeboekt)

#OLD report
    global userHash 
    userHash = userID
    grootboekgroepfile = 'data/grootboekgroep/LION'
    if groepstr != '':
        root = GrootBoekGroep.load(grootboekgroepfile)
        root = root.find(groepstr)
    else: 
        root = GrootBoekGroep.load(grootboekgroepfile)

    body = table_html(root, render, jaar)
    settings = settings_html(root, render, jaar)

    report = {}
#ADD collapse/open all button
#ADD jaar, groep, warning sap ding
    report['settings'] = settings
    report['summary'] = "<a href='../static/figs/"+str(jaar)+"-detailed/1-" + groepstr + ".png' target='_blank'><img class='img-responsive' src='../static/figs/"+str(jaar)+"-detailed/1-"+groepstr+".png'></a>"
    report['body'] = body
    return report

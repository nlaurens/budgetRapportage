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



def parse_order(order, descr, jaar):
    #parse orders in groep:
    KSgroepen = model.loadKSgroepen()
    grootboek =  [s for s in KSgroepen if "BFRE15E01" in s][0]

    root = GrootBoek.load(order, grootboek, jaar, [])
    root.set_totals()

    row = {}
    row['personeelsnummer'] = 'persnNR'
    row['naam'] = 'naam persoon'
    row['begroot'] = 10000
    row['realisatie'] = 20000
    row['resultaat'] = -10000
    return row


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
    html['order'] = 'order'#row['order']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.salaris_table_order_regel(html)


def parse_orders(root, jaar, render, total):
    rows = []
    total['name'] = root.descr
    for order, descr in root.orders.iteritems():
        row = parse_order(order, descr, jaar)
        rows.append(personeel_regel_to_html(row, render))
        total['begroot'] += row['begroot']
        total['realisatie'] += row['realisatie']
        total['resultaat'] += row['resultaat']

    header = {}
    header['row'] = order_regel_to_html(total, render)
    header['id'] = root.name
    header['img'] = "../static/figs/"+str(jaar)+"-detailed/1-"+root.name+".png"

    return rows, header, total


def parse_groep(root, jaar, render):
    groeptotal = {}
    groeptotal['begroot'] = 0
    groeptotal['realisatie'] = 0
    groeptotal['obligo'] = 0
    groeptotal['resultaat'] = 0
    groeprows = []
    for child in root.children:
        childrow, childheader, childgroep, total = parse_groep(child, jaar, render)
#AFHANKELIJK VAN OF DE vorige recursie wel/geen order heeft geparst hier render.salaris_table_groep of render.salaris_table_order gebruiken!
        groeprows.append(render.salaris_table_groep(childrow, childheader, childgroep))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    rows, header, groeptotal = parse_orders(root, jaar, render, groeptotal)
    return rows, header, groeprows, groeptotal


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

    rows, header,total = parse_orders(root, jaar, render, groeptotal)
    table.append(render.salaris_table_groep(rows, header, childtable))

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

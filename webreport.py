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
    totals_order = {}
    totals_order['begroot'] = model.get_plan_totaal(jaar, order)
    totals_order['realisatie'] = -1*(root.totaalGeboektTree)
    totals_order['obligo'] = -1*(root.totaalObligosTree)
    totals_order['resultaat'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) - totals_order['begroot']

#TODO DUMMY code -> order details.
    for i in range(0,1):
        row = {}
        row['personeelsnummer'] = 'todo'
        row['naam'] = 'todo'
        row['begroot'] = 0
        row['realisatie'] = 0
        row['resultaat'] = 0
        html_rows.append(personeel_regel_to_html(row, render))

    header = {}
    header['name'] = descr
    header['userHash'] = userHash
    header['id'] = order
    header['img'] = ('../static/figs/'+str(jaar)+'-detailed/1-' + str(order) + '.png')
    header['begroot'] = table_string(totals_order['begroot'])
    header['realisatie'] =  table_string(totals_order['realisatie'])
    header['obligo'] = table_string(totals_order['obligo'])
    header['resultaat'] = table_string(totals_order['resultaat'])

    order_table = render.salaris_table_order(html_rows, header)
    return order_table, totals_order

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
        groeprows.append(render.salaris_table_groep(childOrderTables, childheader, childgroep))
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
    global userHash 
    userHash = userID
    grootboekgroepfile = 'data/grootboekgroep/LION'
    if groepstr != '':
        root = GrootBoekGroep.load(grootboekgroepfile)
        root = root.find(groepstr)
    else: 
        root = GrootBoekGroep.load(grootboekgroepfile)

    body = table_html(root, render, jaar)
    figs = fig_html(root, render, jaar)
    settings = settings_html(root, render, jaar)

    report = {}
    report['settings'] = settings
    report['figpage'] = figs
    report['summary'] = "<a href='../static/figs/"+str(jaar)+"-detailed/1-" + groepstr + ".png' target='_blank'><img class='img-responsive' src='../static/figs/"+str(jaar)+"-detailed/1-"+groepstr+".png'></a>"
    report['body'] = body
    return report

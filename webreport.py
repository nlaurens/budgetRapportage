"""
TODO
    * Change glyph on collapse like in websalaris!
    * Collapse/Expand orders
    * Use the new model db system. Load all regels from db once. Select afterwards.
"""
import web
from config import config
import OrderGroep
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
    return render.report_table_personeel_regel(html)


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


def parse_order(order, descr, jaar, render):
    #parse orders in groep:

    regels = model.get_regellist_per_table(jaar=[jaar], orders=[order])
    root = GrootBoek.load('BFRE15E01')
    root.assign_regels_recursive(regels)
    root.clean_empty_nodes()
    root.set_totals()

    root.druk_af()

    html_rows = []
    totals_order = {}

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
    header['begroot'] = table_string(root.totaalTree['plan'])
    header['realisatie'] =  table_string(-1*root.totaalTree['geboekt'])
    header['obligo'] = table_string(-1*root.totaalTree['obligo'])
    header['resultaat'] = table_string(-1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) - root.totaalTree['plan'])

    order_table = render.report_table_order(html_rows, header)
    return order_table, root.totaalTree

def parse_orders_in_groep(root, jaar, render, total_groep):
    order_tables = []
    total_groep['name'] = root.descr
    for order, descr in root.orders.iteritems():
        order_table, totaalTree = parse_order(order, descr, jaar, render)
        order_tables.append(order_table)
        total_groep['begroot'] += totaalTree['plan']
        total_groep['realisatie'] += totaalTree['geboekt']
        total_groep['resultaat'] += -1*(totaalTree['geboekt'] + totaalTree['obligo']) - totaalTree['plan']

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
        childtable.append(render.report_table_groep(rows, header, groeprows))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    #add orders of the top group (if any)
    order_tables, header,total = parse_orders_in_groep(root, jaar, render, groeptotal)
    table.append(render.report_table_groep(order_tables, header, childtable))

    body = render.report_table(table)
    return body

def settings_html(root, render, jaar):
    form = 'FORM met daarin jaar'
    buttons = 'BUTTON'
    lastupdate = '2'
    return render.report_settings(lastupdate, buttons, form)


def java_scripts(render, root):
#def java_scripts(render, regelsGeboekt, regelsBegroot):
    #ordersGeboekt = regelsGeboekt.split_by_regel_attributes(['order']).keys()
    #ordersBegroot = regelsBegroot.split_by_regel_attributes(['order']).keys()
    #orders = set(ordersGeboekt + ordersBegroot)

    orders = root.list_orders_recursive()

    return render.salaris_javascripts(orders)


def groep_report(userID, render, groepstr, jaar):
    global userHash
    userHash = userID
    root = OrderGroep.load('LION')
    if groepstr != '':
        root = root.find(groepstr)

    body = table_html(root, render, jaar)
    figs = fig_html(root, render, jaar)
    settings = settings_html(root, render, jaar)
    #javaScripts = java_scripts(render, HRregels['geboekt'], HRregels['begroot']) <- should be used in new db system
    javaScripts = java_scripts(render, root)

    report = {}
    report['settings'] = settings
    report['figpage'] = figs
    report['summary'] = "<a href='../static/figs/"+str(jaar)+"-detailed/1-" + groepstr + ".png' target='_blank'><img class='img-responsive' src='../static/figs/"+str(jaar)+"-detailed/1-"+groepstr+".png'></a>"
    report['body'] = body
    report['javaScripts'] = javaScripts
    return report

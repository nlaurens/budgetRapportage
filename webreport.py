import web
from config import config
import GrootBoekGroep
import GrootBoek
import model
import numpy as np

def table_string(value):
    value = value/1000
    if value == 0 or np.abs(value) < 0.5:
        return ''
    else:
        return ('%.f' % value)

def load_order(order, jaar):
    #parse orders in groep:
    KSgroepen = model.loadKSgroepen()
    grootboek =  [s for s in KSgroepen if "BFRE15E01" in s][0]

    root = GrootBoek.load(order, grootboek, jaar, [])
    root.set_totals()

    row = {}
    row['name'] = order
    row['begroot'] = model.get_plan_totaal(jaar, order)
    row['realisatie'] = -1*(root.totaalGeboektTree)
    row['obligo'] = -1*(root.totaalObligosTree)
    row['resultaat'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) - row['begroot']
    return row

def row_to_html(row, render):
    html = row.copy()
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['obligo'] =  table_string(row['obligo'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.report_table_row(html)

def parse_orders(root, jaar, render):
    rows = []
    groep = {}
    groep['name'] = root.descr
    groep['begroot'] = 0
    groep['realisatie'] = 0
    groep['obligo'] = 0
    groep['resultaat'] = 0
    for order, descr in root.orders.iteritems():
        row = load_order(order, jaar)
        groep['begroot'] += row['begroot']
        groep['realisatie'] += row['realisatie']
        groep['obligo'] += row['obligo']
        groep['resultaat'] += row['resultaat']
        rows.append(row_to_html(row, render))

    header = {}
    header['row'] = row_to_html(groep, render)
    header['id'] = root.name
    header['img'] = "../static/figs/"+str(jaar)+"-detailed/1-"+root.name+".png"

    return rows, header


def groep_report(render, groepstr, jaar):
    grootboekgroepfile = 'data/grootboekgroep/LION'
    root = GrootBoekGroep.load(grootboekgroepfile).find(groepstr)

    table = []
    childtable = []
    for child in root.children:
        rows, header = parse_orders(child, jaar, render)
        childtable.append(render.report_table_groep(rows, header, ''))

    rows, header = parse_orders(root, jaar, render)
    table.append(render.report_table_groep(rows, header, childtable))

    body = render.report_table(table)

    report = {}
    report['settings'] = 'settings!!'
    report['summary'] = "<a href='../static/figs/"+str(jaar)+"-detailed/1-" + groepstr + ".png' target='_blank'><img class='img-responsive' src='../static/figs/"+str(jaar)+"-detailed/1-"+groepstr+".png'></a>"

    report['body'] = body
    return report

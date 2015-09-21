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

def load_order(order, descr, jaar):
    #parse orders in groep:
    KSgroepen = model.loadKSgroepen()
    grootboek =  [s for s in KSgroepen if "BFRE15E01" in s][0]

    root = GrootBoek.load(order, grootboek, jaar, [])
    root.set_totals()

    row = {}
    row['name'] = descr
    row['order'] = order
    row['begroot'] = model.get_plan_totaal(jaar, order)
    row['realisatie'] = -1*(root.totaalGeboektTree)
    row['obligo'] = -1*(root.totaalObligosTree)
    row['resultaat'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) - row['begroot']
    return row

def row_to_html(row, render, groep=False):
    html = row.copy()
    if groep:
        html['name'] = row['name']
    else:
#TODO USERSTRING
        html['name'] = "<a href='/view/"+userHash+"/"+str(row['order'])+"'>"+row['name']+ "</a>"

    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['obligo'] =  table_string(row['obligo'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.report_table_row(html)

def parse_orders(root, jaar, render, total):
    rows = []
    total['name'] = root.descr
    for order, descr in root.orders.iteritems():
        row = load_order(order, descr, jaar)
        rows.append(row_to_html(row, render))
        total['begroot'] += row['begroot']
        total['realisatie'] += row['realisatie']
        total['obligo'] += row['obligo']
        total['resultaat'] += row['resultaat']

    header = {}
    header['row'] = row_to_html(total, render, groep=True)
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
        groeprows.append(render.report_table_groep(childrow, childheader, childgroep))
        groeptotal['begroot'] += total['begroot']
        groeptotal['realisatie'] += total['realisatie']
        groeptotal['obligo'] += total['obligo']
        groeptotal['resultaat'] += total['resultaat']

    rows, header, groeptotal = parse_orders(root, jaar, render, groeptotal)
    return rows, header, groeprows, groeptotal

def groep_report(userID, render, groepstr, jaar):
    global userHash 
    userHash = userID
    grootboekgroepfile = 'data/grootboekgroep/LION'
    if groepstr != '':
        root = GrootBoekGroep.load(grootboekgroepfile)
        root = root.find(groepstr)
    else: 
        root = GrootBoekGroep.load(grootboekgroepfile)

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

    rows, header,total = parse_orders(root, jaar, render, groeptotal)
    table.append(render.report_table_groep(rows, header, childtable))

    body = render.report_table(table)
    figs = ''
    if not root.children:
        graphs = []
        i = 0
        for order, descr in root.orders.iteritems():
            graph = {}
            graph['link'] = ('../view/' + userHash + '/' + str(order))
            graph['png'] = ('../static/figs/'+str(jaar)+'-detailed/1-' + str(order) + '.png')
            if i%2:
                graph['spacer'] = '</tr><tr>'
            else:
                graph['spacer'] = ''
            graphs.append(graph)
            i +=1

        figs = render.report_figpage(graphs)

    report = {}
    report['settings'] = 'settings!!'
    report['summary'] = "<a href='../static/figs/"+str(jaar)+"-detailed/1-" + groepstr + ".png' target='_blank'><img class='img-responsive' src='../static/figs/"+str(jaar)+"-detailed/1-"+groepstr+".png'></a>"
    report['body'] = body
    report['figpage'] = figs
    return report

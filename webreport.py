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
from webgraph import generate_url

import webpage
from webpage import Webpage

class Report(Webpage):
    def __init__(self, userHash):
        Webpage.__init__(self, userHash)

        #subclass specific
        self.title = 'Budget Report'
        self.module = 'report'
        self.webrender = web.template.render('templates/report/')

        #Forms


    def render_body(self):
#TODO root, jaar naar init en self.params
        self.groepstr = ''
        self.jaar = 2016
#TODO config
        self.root = OrderGroep.load('LION')
        if self.groepstr != '':
            self.root = self.root.find(groepstr)

#TODO lijkt erop dat dit recursie is die we in de render_body all kunnen doen
        body = self.render_table_html()
        figs = 'dummy figs'#fig_html(root, render, jaar)
        settings = 'dummy settings'#settings_html(root, render, jaar)
        #javaScripts = java_scripts(render, HRregels['geboekt'], HRregels['begroot']) <- should be used in new db system
        javaScripts = 'dummy-java-'#java_scripts(render, root)

        report = {}
        report['settings'] = settings
        report['figpage'] = figs
        url = 'dummy url'#graph_url(userHash, jaar, 'realisatie', groepstr)
        report['summary'] = "<a href='"+url+"' target='_blank'><img class='img-responsive' src='"+url+"'></a>"
        report['body'] = body
        report['javaScripts'] = javaScripts

        self.body = self.webrender.report(report)

        return report


    def render_table_html(self):
        table = []
        childtable = []
        groeptotal = {}
        groeptotal['begroot'] = 0
        groeptotal['realisatie'] = 0
        groeptotal['obligo'] = 0
        groeptotal['resultaat'] = 0
        for child in self.root.children:
            rows, header, groeprows, total = self.parse_groep(child)
            childtable.append(self.webrender.report_table_groep(rows, header, groeprows))
            groeptotal['begroot'] += total['begroot']
            groeptotal['realisatie'] += total['realisatie']
            groeptotal['obligo'] += total['obligo']
            groeptotal['resultaat'] += total['resultaat']

        #add orders of the top group (if any)
        order_tables, header,total = self.parse_orders_in_groep(self.root, groeptotal)
        table.append(self.webrender.report_table_groep(order_tables, header, childtable))

        body = self.webrender.report_table(table)
        return body


    def parse_groep(self, root):
        groeptotal = {}
        groeptotal['begroot'] = 0
        groeptotal['realisatie'] = 0
        groeptotal['obligo'] = 0
        groeptotal['resultaat'] = 0
        groeprows = []
        for child in root.children:
            childOrderTables, childheader, childgroep, total = self.parse_groep(child)
            groeprows.append(self.webrender.report_table_groep(childOrderTables, childheader, childgroep))
            groeptotal['begroot'] += total['begroot']
            groeptotal['realisatie'] += total['realisatie']
            groeptotal['obligo'] += total['obligo']
            groeptotal['resultaat'] += total['resultaat']

        order_tables, groepheader, groeptotal = self.parse_orders_in_groep(root, groeptotal)
        return order_tables, groepheader, groeprows, groeptotal


    def parse_orders_in_groep(self, root, total_groep):
        order_tables = []
        total_groep['name'] = root.descr
        for order, descr in root.orders.iteritems():
            order_table, totaalTree = self.parse_order(order, descr)
            order_tables.append(order_table)
            total_groep['begroot'] += totaalTree['plan']
            total_groep['realisatie'] += totaalTree['geboekt'] + totaalTree['obligo']
            total_groep['resultaat'] += totaalTree['plan'] - totaalTree['geboekt'] - totaalTree['obligo']

        groep_header = {}
        groep_header['row'] = self.groep_regel_to_html(total_groep)
        groep_header['id'] = root.name
        groep_header['img'] = generate_url(self.userHash, self.jaar, 'realisatie', root.name)

        return order_tables, groep_header, total_groep


    def parse_order(self, order, descr):
        #parse orders in groep:

        regels = model.get_regellist_per_table(jaar=[self.jaar], orders=[order])
#TODO  In config params!!
        root = GrootBoek.load('BFRE15')
        root = root.find('BFRE15E01')
        root.assign_regels_recursive(regels)
        root.clean_empty_nodes()
        root.set_totals()

        html_rows = []
        totals_order = {}

        for child in root.children:
            for child in child.children:
                row = {}
                row['grootboek'] = child.descr
                row['begroot'] = child.totaalTree['plan']
                row['realisatie'] = child.totaalTree['geboekt'] + child.totaalTree['obligo']
                row['resultaat'] = child.totaalTree['plan']   - (child.totaalTree['geboekt'] + child.totaalTree['obligo'])
                html_rows.append(self.grootboek_regel_to_html(row))

        header = {}
        header['name'] = descr + '(%s)' % order
        header['userHash'] = self.userHash
        header['id'] = order
        header['img'] = generate_url(self.userHash, self.jaar, 'realisatie', order)
        header['begroot'] = table_string(root.totaalTree['plan'])
        header['realisatie'] =  table_string(root.totaalTree['geboekt'] + root.totaalTree['obligo'])
        header['resultaat'] = table_string(root.totaalTree['plan'] - root.totaalTree['geboekt'] - root.totaalTree['obligo'])

        order_table = self.webrender.report_table_order(html_rows, header)
        return order_table, root.totaalTree


    def grootboek_regel_to_html(self, row):
        html = row.copy()
        html['grootboek'] = row['grootboek']
        html['begroot'] = table_string(row['begroot'])
        html['realisatie'] =  table_string(row['realisatie'])
        html['resultaat'] = table_string(row['resultaat'])
        return self.webrender.report_table_grootboek_regel(html)


    def groep_regel_to_html(self, row):
        html = row.copy()
#TODO
        html['name'] = row['name']
        html['begroot'] = table_string(row['begroot'])
        html['realisatie'] =  table_string(row['realisatie'])
        html['resultaat'] = table_string(row['resultaat'])
        return self.webrender.report_table_groep_regel(html)
# FROM OLD SERVER.PY - render:
        #jaar, periode, groep = self.get_params()
        #report = webreport.groep_report(userHash, render, groep, jaar)

   # def get_params(self):

   #     try:
   #         jaar = int(web.input()['jaar'])
   #     except:
   #         jaar = config["currentYear"]

   #     try:
   #         periode = web.input()['periode']
   #     except:
   #         periode = '0,1,2,3,4,5,6,7,8,9,10,11,12'

   #     try:
   #         groep = web.input()['groep']
   #     except:
   #         groep = 'TOTAAL'

   #     return jaar, periode, groep


###########################################################
#Functions
###########################################################
def table_string(value):
    value = value/1000
    if value == 0 or np.abs(value) < 0.5:
        return '&nbsp;'
    else:
        return ('%.f' % value)


def order_regel_to_html(row, render):
    html = row.copy()
#TODO
    html['order'] = row['name']
    html['begroot'] = table_string(row['begroot'])
    html['realisatie'] =  table_string(row['realisatie'])
    html['resultaat'] = table_string(row['resultaat'])
    return render.report_table_order_regel(html)


def fig_html(root, render, jaar):
    figs = ''
    if not root.children:
        graphs = []
        i = 0
        for order, descr in root.orders.iteritems():
            graph = {}
            graph['link'] = ('../view/' + userHash + '/' + str(order))
            graph['png'] = graph_url(userHash, jaar, 'realisatie', order)
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



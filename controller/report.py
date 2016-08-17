import web
from web import form
import numpy as np

from controller import Controller
from functions import moneyfmt

import model.ksgroup
import model.ordergroup
import model.regels


class Report(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Report'
        self.module = 'report'
        self.webrender = web.template.render('webpages/report/', cache=False)

        # Salaris specific:
        # Report specific:
        self.jaar = int(web.input(year=self.config["currentYear"])['year'])
# TODO config
        self.subgroep = str(web.input(subgroep='TOTAAL')['subgroep'])
        self.ordergroep = str(web.input(ordergroep='LION')['ordergroep'])
        self.flat = False 
        if web.input().has_key('flat'):
            self.flat = True
        self.expandOrders = bool(int(web.input(expandOrders='0')['expandOrders']))

        ordergroup = model.ordergroup.load(self.ordergroep)
        ordergroup = ordergroup.find(self.subgroep)
        self.root = ordergroup

        self.orders = self.root.list_orders_recursive().keys()

        regels = model.regels.load(years_load=[self.jaar], orders_load=self.orders)
        self.regels = regels.split(['ordernummer', 'tiepe'])

        # Forms
        dropdown_options = self. dropdown_options()
        self.form_settings_simple = form.Form(
            form.Dropdown('year', dropdown_options['years'], 
                          description='Year', value=self.jaar),
            form.Checkbox('flat', description='ignore subgroups'),
            form.Button('submit', value='report_settings')
        )

    def process_sub(self):
        self.create_bread_crums()

        report = {}
        report['name'] = self.root.descr
        report['tables'], totals = self.render_tables()
        report['figpage'] = self.render_fig_html()
        report['settings'] = self.render_settings_html()
        report['javaScripts'] = self.render_java_scripts()
        for key,value in totals.iteritems():
            totals[key] = moneyfmt(value, keur=True)
        report['summary'] = self.webrender.summary(totals)

        self.body = self.webrender.report(report)

    def render_tables(self):
        tables = []

        totals = {}
        totals['begroot'] = 0
        totals['realisatie'] = 0
        totals['obligo'] = 0
        totals['resultaat'] = 0
        
        if self.root.children:
            for ordergroep in self.root.children:
                if self.flat and ordergroep.children:
                    ordergroep = ordergroep.flat_copy()
                top_table, total_table = self.render_top_table(ordergroep)
                totals['begroot'] += total_table['begroot']
                totals['realisatie'] += total_table['realisatie']
                totals['obligo'] += total_table['obligo']
                totals['resultaat'] += total_table['resultaat']
                tables.append(top_table)
        else:
            top_table, totals = self.render_top_table(self.root)
            tables.append(top_table)

        return tables, totals

    def create_bread_crums(self):
        groep = self.root
        bread_crum = [{'title': groep.descr, 'url': groep.name, 'class': 'active'}]
        while groep.parent:
            groep = groep.parent
            link = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroep, groep.name)
            bread_crum.append({'title': groep.descr, 'url': link, 'class': ''})
        self.breadCrum = reversed(bread_crum)

    def render_top_table(self, ordergroep):
        table = []
        childtable = []
        groeptotal = {}
        groeptotal['begroot'] = 0
        groeptotal['realisatie'] = 0
        groeptotal['obligo'] = 0
        groeptotal['resultaat'] = 0

        for child in ordergroep.children:
            rows, header, groeprows, total = self.parse_groep(child)
            childtable.append(self.webrender.table_groep(rows, header, groeprows))
            groeptotal['begroot'] += total['begroot']
            groeptotal['realisatie'] += total['realisatie']
            groeptotal['obligo'] += total['obligo']
            groeptotal['resultaat'] += total['resultaat']

        # add orders of the top group (if any)
        order_tables, header, total = self.parse_orders_in_groep(ordergroep, groeptotal)

        top_table = self.webrender.table(order_tables, header, childtable)
        return top_table, groeptotal

    def parse_groep(self, root):
        groeptotal = {}
        groeptotal['begroot'] = 0
        groeptotal['realisatie'] = 0
        groeptotal['obligo'] = 0
        groeptotal['resultaat'] = 0
        groeprows = []
        for child in root.children:
            child_order_tables, childheader, childgroep, total = self.parse_groep(child)
            groeprows.append(self.webrender.table_groep(child_order_tables, childheader, childgroep))
            groeptotal['begroot'] += total['begroot']
            groeptotal['realisatie'] += total['realisatie']
            groeptotal['obligo'] += total['obligo']
            groeptotal['resultaat'] += total['resultaat']

        order_tables, groepheader, groeptotal = self.parse_orders_in_groep(root, groeptotal)
        return order_tables, groepheader, groeprows, groeptotal

    def parse_orders_in_groep(self, root, total_groep):
        order_tables = []
        total_groep['id'] = root.name
        total_groep['name'] = root.descr
        for order, descr in root.orders.iteritems():
            order_table, totaal_tree = self.parse_order(order, descr)
            order_tables.append(order_table)
            total_groep['begroot'] += totaal_tree['plan']
            total_groep['realisatie'] += totaal_tree['geboekt'] + totaal_tree['obligo']
            total_groep['resultaat'] += totaal_tree['plan'] - totaal_tree['geboekt'] - totaal_tree['obligo']

        groep_header = {}
        regel_html_ready = self.groep_regel_to_html(total_groep)  
        groep_header['panel_header'] = self.webrender.table_header(regel_html_ready)   # row for panel-header - if top group
        groep_header['row'] = self.webrender.table_groep_regel(regel_html_ready)
        groep_header['id'] = root.name
        groep_header['img'] = self.url_graph(self.jaar, 'realisatie', root.name)

        return order_tables, groep_header, total_groep

    def parse_order(self, order, descr):
        # parse orders in groep:
        regels = {}
        if order in self.regels:
            regels = self.regels[order]

# TODO  In config params!!
        root = model.ksgroup.load('BFRE15')
        root = root.find('BFRE15E01')

# TODO prevent this. regels is now a dictionary not a single regellist.
        from model.budget import RegelList
        regel_list = RegelList()  # Create 1 regellist and not a dict per type
        for key, regellist in regels.iteritems():
            regel_list.extend(regellist)
        regels = regel_list

        root.assign_regels_recursive(regels)
        root.clean_empty_nodes()
        root.set_totals()

        html_rows = []
        totals_order = {}

        for child_root in root.children:
            for child in child_root.children:
                row = {}
                row['grootboek'] = child.descr
                row['begroot'] = child.totaalTree['plan']
                row['realisatie'] = child.totaalTree['geboekt'] + child.totaalTree['obligo']
                row['resultaat'] = child.totaalTree['plan'] - (child.totaalTree['geboekt'] + child.totaalTree['obligo'])
                html_rows.append(self.order_regel_to_html(row))

        begroot = root.totaalTree['plan']
        realisatie = root.totaalTree['geboekt'] + root.totaalTree['obligo']
        header = {}
        header['name'] = '%s (%s)' % (descr, order)
        header['link'] = '/view/%s?order=%s' % (self.userHash, order)
        header['userHash'] = self.userHash
        header['id'] = order
        header['img'] = self.url_graph(self.jaar, 'realisatie', order)
        header['begroot'] = moneyfmt(root.totaalTree['plan'], keur=True)
        header['realisatie'] = moneyfmt(realisatie, keur=True)
        if begroot == 0:
            header['realisatie_perc'] = str(0)
        else:
            header['realisatie_perc'] = moneyfmt(realisatie/begroot*100)
        header['resultaat'] = moneyfmt(root.totaalTree['plan'] - root.totaalTree['geboekt'] - root.totaalTree['obligo'], keur=True)

        order_table = self.webrender.table_order(html_rows, header, self.expandOrders)
        return order_table, root.totaalTree

    # Renders the kostensoort per order
    def order_regel_to_html(self, row):
        html = row.copy()
        html['grootboek'] = row['grootboek']
        html['begroot'] = moneyfmt(row['begroot'], keur=True)
        html['realisatie'] = moneyfmt(row['realisatie'], keur=True)
        if row['begroot'] == 0:
            html['realisatie_perc'] = 0
        else:
            html['realisatie_perc'] = moneyfmt(row['realisatie']/row['begroot']*100)
        html['resultaat'] = moneyfmt(row['resultaat'], keur=True)
        return self.webrender.table_order_regel(html)

    def groep_regel_to_html(self, row):
        html = row.copy()
        html['name'] = row['name']
        html['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroep, row['id'])
        html['begroot'] = moneyfmt(row['begroot'], keur=True)
        html['realisatie'] = moneyfmt(row['realisatie'], keur=True)
        if row['begroot'] == 0:
            html['realisatie_perc'] = 0
        else:
            html['realisatie_perc'] = moneyfmt(row['realisatie']/row['begroot']*100)
        html['resultaat'] = moneyfmt(row['resultaat'], keur=True)
        return html

# TODO layout!
    def render_fig_html(self):
        figs = ''
        if not self.root.children:
            graphs = []
            i = 0
            for order, descr in self.root.orders.iteritems():
                graph = {}
                graph['link'] = ('../view/' + self.userHash + '/' + str(order))
                graph['png'] = self.url_graph(self.jaar, 'realisatie', order)
                # if i%2:
                #    graph['spacer'] = '</tr><tr>'
                # else:
                #    graph['spacer'] = ''
                graphs.append(graph)
                i += 1

            figs = self.webrender.figpage(graphs)
            return figs
        else:
            return None

# TODO replace dummy vasr
    def render_settings_html(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)

    def render_java_scripts(self):
        expand_items = self.orders
        expand_items.extend(self.root.list_groepen_recursive().values())
        return self.webrender.javascripts(expand_items)


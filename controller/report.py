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
#TODO naar settings form and remove self.jaar
        self.years = [2016, 2017]  
# TODO config

        self.flat = False 
        if web.input().has_key('flat'):
            self.flat = True
       
        self.expand_orders = False 
        if web.input().has_key('expand_orders'):
            self.expand_orders = True

        self.ordergroup_file = str(web.input(ordergroep='LION')['ordergroep'])
        ordergroup = model.ordergroup.load(self.ordergroup_file)
        self.ordergroup = ordergroup.find(str(web.input(subgroep='TOTAAL')['subgroep']))
        self.orders = self.ordergroup.list_orders_recursive().keys()

        regels = model.regels.load(years_load=[self.jaar], orders_load=self.orders)
        self.regels = regels.split(['ordernummer', 'tiepe'])

        # Forms
        dropdown_options = self. dropdown_options()
        self.form_settings_simple = form.Form(
            form.Dropdown('year', dropdown_options['years'], 
                          description='Year', value=self.jaar),
            form.Checkbox('flat', description='ignore subgroups'),
            form.Checkbox('expand_orders', description='Details orders'),
            form.Button('submit', value='report_settings')
        )

    def process_sub(self):
        self.create_bread_crums()  # sets the breadcrumbs for the header

        data = self.construct_data() 
        self.convert_data_to_str(data)

        report = {}
        report['name'] = self.ordergroup.descr
        report['tables'] = self.render_tables(data)
        report['figpage'] = self.render_fig_html()
        report['settings'] = self.render_settings_html()
        report['javaScripts'] = self.render_java_scripts()
        report['summary'] = self.webrender.summary(data['total'])
        self.body = self.webrender.report(report)

    def create_bread_crums(self):
        groep = self.ordergroup
        bread_crum = [{'title': groep.descr, 'url': groep.name, 'class': 'active'}]
        while groep.parent:
            groep = groep.parent
            link = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup_file, groep.name)
            bread_crum.append({'title': groep.descr, 'url': link, 'class': ''})
        self.breadCrum = reversed(bread_crum)

    def construct_data(self):   
        regels = model.regels.load(years_load=self.years, orders_load=self.orders) 
        regels_order_tiepe = regels.split(['ordernummer', 'jaar', 'tiepe'])

        data = {}  # holds all data needed to build the view
        data['total'] = {}
        for year in self.years:
            data['total'][year] = {'geboekt':0, 'obligo':0, 'plan':0, 'realisatie':0, 'resultaat':0, 'realisatie_perc':0}

        for order in regels_order_tiepe.keys():
            data[order] = {}
            for year in self.years:
                data[order][year] = {}
                data[order][year] = {'geboekt':0, 'obligo':0, 'plan':0, 'realisatie':0, 'resultaat':0, 'realisatie_perc':0}
            for year in regels_order_tiepe[order].keys():
                for tiepe in regels_order_tiepe[order][year].keys():
                    data[order][year][tiepe] = regels_order_tiepe[order][year][tiepe].total()
                    data['total'][year][tiepe] += data[order][year][tiepe]

                data[order][year]['resultaat'] = data[order][year]['plan'] - data[order][year]['realisatie']
                data['total'][year]['resultaat'] += data[order][year]['resultaat']
                data[order][year]['realisatie'] = data[order][year]['geboekt'] + data[order][year]['obligo']
                data['total'][year]['realisatie'] += data[order][year]['realisatie']

                if data[order][year]['plan'] != 0:
                    data[order][year]['realisatie_perc'] = data[order][year]['realisatie'] / data[order][year]['plan'] * 100
                else:
                    data[order][year]['realisatie_perc'] = 0

                if data['total'][year]['plan'] != 0:
                    data['total'][year]['realisatie_perc'] = data['total'][year]['realisatie'] / data['total'][year]['plan'] * 100
                else:
                    data['total'][year]['realisatie_perc'] = 0

        return data

    def convert_data_to_str(self, data):
        for year, tiepes in data['total'].iteritems():
            for tiepe, value in tiepes.iteritems():
                if tiepe == 'realisatie_perc':
                    data['total'][year][tiepe] = moneyfmt(value)
                else:
                    data['total'][year][tiepe] = moneyfmt(value, keur=True)

        for order in data.keys():
            for year in data[order].keys():
                for tiepe, value in data[order][year].iteritems():
                    if tiepe == 'realisatie_perc':
                        data[order][year][tiepe] = moneyfmt(value)
                    else:
                        data[order][year][tiepe] = moneyfmt(value, keur=True)

    def render_tables(self, data):
        tables = []
        if self.ordergroup.children:
            for ordergroep in self.ordergroup.children:
                if self.flat and ordergroep.children:
                    ordergroep = ordergroep.flat_copy()
                top_table = self.render_top_table(ordergroep, data)
                tables.append(top_table)
        else:
            top_table = self.render_top_table(self.ordergroup, data)
            tables.append(top_table)

        return tables

    def render_top_table(self, ordergroep, data):
        table = []
        childtable = []

        for child in ordergroep.children:
            pass
            #rows, header, groeprows, total = self.parse_groep(child)
            #childtable.append(self.webrender.table_groep(rows, header, groeprows))
            #groeptotal['begroot'] += total['begroot']
            #groeptotal['realisatie'] += total['realisatie']
            #groeptotal['obligo'] += total['obligo']
            #groeptotal['resultaat'] += total['resultaat']

        # add orders of the top group (if any)
        order_rows = []
        for order, descr in ordergroep.orders.iteritems():
            row = {}
            row['id'] = 'ID'
            row['graph'] = 'GRAPH'
            row['link'] = 'link'
            row['name'] = descr
            row['begroot'] = 'begroot'
            row['realisatie'] = 'realisate'
            row['realisatie_perc'] = 'realisate_perc'
            row['resultaat'] = 'resultaat'
            order_rows.append(row)

        order_table = self.webrender.table_order(order_rows, self.expand_orders)

        header = {}
        header['name'] = ordergroep.descr
        header['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup_file, ordergroep.name)

        top_table = self.webrender.table(order_table, header, childtable)
        return top_table


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
        groep_header['row'] = self.webrender.table_groep_regel(regel_html_ready)
        groep_header['id'] = root.name
        groep_header['img'] = self.url_graph(self.jaar, 'realisatie', root.name)

        return order_tables, groep_header, total_groep

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

        #subgroepen van subgroepen
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
        html['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup, row['id'])
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
        if not self.ordergroup.children:
            graphs = []
            i = 0
            for order, descr in self.ordergroup.orders.iteritems():
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
        expand_items.extend(self.ordergroup.list_groepen_recursive().values())
        return self.webrender.javascripts(expand_items)


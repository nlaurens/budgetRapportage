import web
from web import form
import numpy as np

from controller import Controller
from functions import moneyfmt

import model.ksgroup
import model.ordergroup
import model.regels


#TODO: get start/stop years from model and take latest year and years before that (if avail.)
#TODO: fig page.. now what do we do with the years?
#TODO: groups en orders in 1 table renderen en bij de jaartallen de link naar de hoofdgroep grpahs zetten
#TODO: jaartallen in summary de link naar de graphs
#TODO: 1 kolom extra in elke tabel en daarin het grafiekje van de jaren zetten zodat het goed te zien is
# grafiek: x = jan/dec, y = 0 tot 100% realisatie t.o.v. begroting (dus 1 lijn begroting stippel de rest in kleurtjes
# met in legenda eronder de absolute getallen in realisatie


class Report(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Report'
        self.module = 'report'
        self.webrender = web.template.render('webpages/report/', cache=False)

        # Salaris specific:
        # Report specific:
        year_start = int(web.input(year_start=self.config["currentYear"])['year_start'])
        year_stop = int(web.input(year_stop=self.config["currentYear"])['year_stop'])

        self.years = range(year_start, year_stop+1)

        self.flat = False
        if web.input().has_key('flat'):
            self.flat = True

        self.ordergroup_file = str(web.input(ordergroep='LION')['ordergroep'])
        ordergroup = model.ordergroup.load(self.ordergroup_file)
        self.ordergroup = ordergroup.find(str(web.input(subgroep='TOTAAL')['subgroep']))
        self.orders = self.ordergroup.list_orders_recursive().keys()

        # Forms
        dropdown_options = self. dropdown_options()
        self.form_settings_simple = form.Form(
            form.Dropdown('year_start', dropdown_options['years'],
                          description='From', value=year_start),
            form.Dropdown('year_stop', dropdown_options['years'],
                          description='To', value=year_stop),
            form.Checkbox('flat', description='Show all orders in groups:'),
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
        report['summary'] = self.webrender.summary(data[self.ordergroup.name])
        self.body = self.webrender.report(report)

    def create_bread_crums(self):
        groep = self.ordergroup
        bread_crum = [{'title': groep.descr, 'url': groep.name, 'class': 'active'}]
        while groep.parent:
            groep = groep.parent
            link = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup_file, groep.name)
            bread_crum.append({'title': groep.descr, 'url': link, 'class': ''})
        self.breadCrum = reversed(bread_crum)

    """
        Constructs all the data that is needed for the report:
        data{
          <order#/ordergroup-descr>: {<year1>: {geboekt/obligo/etc./}, <year2>: {..}
          ,,
        }
    """
    def construct_data(self):
        regels = model.regels.load(years_load=self.years, orders_load=self.orders)
        regels_order_tiepe = regels.split(['ordernummer', 'jaar', 'tiepe'])

        data = {}  # construct data dictand preload all possible keys
        for order in self.orders:
            data[order] = {}
            for year in self.years:
                data[order][year] = {}
                data[order][year] = {'geboekt':0, 'obligo':0, 'plan':0, 'realisatie':0, 'resultaat':0, 'realisatie_perc':0}

        # load data for all orders
        for order in regels_order_tiepe.keys():
            for year in regels_order_tiepe[order].keys():
                for tiepe in regels_order_tiepe[order][year].keys():
                    data[order][year][tiepe] = regels_order_tiepe[order][year][tiepe].total()

                data[order][year]['realisatie'] = data[order][year]['geboekt'] + data[order][year]['obligo']
                data[order][year]['resultaat'] = data[order][year]['plan'] - data[order][year]['realisatie']

                if data[order][year]['plan'] != 0:
                    data[order][year]['realisatie_perc'] = data[order][year]['realisatie'] / data[order][year]['plan'] * 100
                else:
                    data[order][year]['realisatie_perc'] = 0

        # load data for all groups:
        ordergroups = self.ordergroup.list_groups()
        for group in ordergroups:
            data[group.name] = {}
            for year in self.years:
                data[group.name][year] = {}
                for tiepe in ['begroot', 'plan', 'resultaat', 'realisatie', 'realisatie_perc']:
                    data[group.name][year][tiepe] = 0

                    # add subgroup values
                    for subgroup in group.children:
                        if tiepe in data[subgroup.name][year]:
                            data[group.name][year][tiepe] += data[subgroup.name][year][tiepe]

                    # add orders from this grop
                    for order in group.orders:
                        if tiepe in data[order][year]:
                            data[group.name][year][tiepe] += data[order][year][tiepe]

        return data

    def convert_data_to_str(self, data):
        # orders
        for key in data.keys():
            order = key
            for year in data[order].keys():
                for tiepe, value in data[order][year].iteritems():
                    if tiepe == 'realisatie_perc':
                        data[order][year][tiepe] = moneyfmt(value)
                    else:
                        data[order][year][tiepe] = moneyfmt(value, keur=True)

    def render_fig_html(self):
        figs = ''
        if not self.ordergroup.children:
            graphs = []
            i = 0
            for order, descr in self.ordergroup.orders.iteritems():
                graph = {}
                graph['link'] = ('../view/' + self.userHash + '/' + str(order))
                graph['png'] = self.url_graph(self.years[0], 'realisatie', order)
                graphs.append(graph)
                i += 1

            figs = self.webrender.figpage(graphs)
            return figs
        else:
            return None

    def render_settings_html(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)

    def render_java_scripts(self):
        expand_items = self.orders
        ordergroup_list = self.ordergroup.list_groups()
        for group in ordergroup_list:
            expand_items.append(group.name)
        return self.webrender.javascripts(expand_items)

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

    def render_top_table(self, ordergroup, data):
        header = {}
        header['name'] = ordergroup.descr
        header['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup_file, ordergroup.name)

        # sub tables
        group_table = None
        if ordergroup.children:
            group_table = self.render_group_table(ordergroup, data)

        # add orders of the top group (if any)
        order_table = None
        if ordergroup.orders:
            order_table = self.render_order_table(data, ordergroup)

        top_table = self.webrender.table(order_table, header, group_table)
        return top_table

    def render_group_table(self, ordergroup, data):
        group_rows = []
        for subgroup in ordergroup.children:
            row = {}
            row['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroup_file, subgroup.name)
            row['name'] = subgroup.descr
            row['subgroup'] = 'SUBGROUP'  # replace by self.render_group_table

            for year in self.years:
                row[year] = {}
                row[year]['id'] = '%s-%s' % (year, subgroup.name)
                row[year]['graph'] = self.url_graph(year, 'realisatie', subgroup.name)
                row[year]['plan'] = data[subgroup.name][year]['plan']
                row[year]['realisatie'] = data[subgroup.name][year]['realisatie']
                row[year]['realisatie_perc'] = data[subgroup.name][year]['realisatie_perc']
                row[year]['resultaat'] = data[subgroup.name][year]['resultaat']
            group_rows.append(row)


        totals = data[ordergroup.name]

        # add orders of the top group
        order_table = None
        if ordergroup.orders:
            order_table = self.render_order_table(data, ordergroup)

        sub_table = self.webrender.table_group(self.years, totals, group_rows, order_table)
        return sub_table

    def render_order_table(self, data, ordergroup):
        order_rows = []
        for order, descr in ordergroup.orders.iteritems():
            row = {}
            row['link'] = '/view/%s?order=%s' % (self.userHash, order)
            row['name'] = descr
            row['order'] = order

            for year in self.years:
                row[year] = {}
                row[year]['id'] = '%s-%s' % (year, order)
                row[year]['graph'] = self.url_graph(year, 'realisatie', order)
                row[year]['plan'] = data[order][year]['plan']
                row[year]['realisatie'] = data[order][year]['realisatie']
                row[year]['realisatie_perc'] = data[order][year]['realisatie_perc']
                row[year]['resultaat'] = data[order][year]['resultaat']
            order_rows.append(row)

        totals = data[ordergroup.name]
        order_table = self.webrender.table_order(self.years, order_rows, totals)
        return order_table



import web
from web import form

import model.ordergroup
import model.regels
from controller import Controller
from functions import moneyfmt
from config import config


class Report(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Report'
        self.module = 'report'
        self.webrender = web.template.render('webpages/report/', cache=False)

        # Report specific:
        years = model.regels.years()
        if config['currentYear'] in years:
            index = years.index(config['currentYear'])
            year_stop_def = years[index]
            year_start_def = years[index-1]
        else:
            year_start_def = years[0]
            year_stop_def = years[0]

        year_start = int(web.input(year_start=year_start_def)['year_start'])
        year_stop = int(web.input(year_stop=year_stop_def)['year_stop'])
        self.years = range(min(year_start, year_stop), max(year_start, year_stop)+1)

        self.flat = False
        if web.input().has_key('flat'):
            self.flat = True

        self.ordergroup_file = str(web.input(ordergroep='LION')['ordergroep'])
        ordergroup = model.ordergroup.load(self.ordergroup_file)
        self.ordergroup = ordergroup.find(str(web.input(subgroep='TOTAAL')['subgroep']))
        self.orders = self.ordergroup.list_orders_recursive().keys()

        # Forms
        dropdown_options = self.dropdown_options()
        self.form_settings_simple = form.Form(
            form.Dropdown('year_start', dropdown_options['years'],
                          description='From', value=year_start),
            form.Dropdown('year_stop', dropdown_options['years'],
                          description='To', value=year_stop),
            form.Checkbox('flat', description='Show all orders in groups:'),
            form.Button('submit', value='report_settings')
        )


    def authorized(self):
        if model.users.check_permission(['report']) and model.users.check_ordergroup(self.ordergroup_file, self.ordergroup.name):
            return True

        return False


    def process_sub(self):
        self.create_bread_crums()  # sets the breadcrumbs for the header

        data = self.construct_data()
        self.convert_data_to_str(data)

        report = {}
        report['name'] = self.ordergroup.descr
        report['tables'] = self.render_tables(data)
        report['figpage'] = self.render_fig()
        report['settings'] = self.render_settings()
        report['javaScripts'] = self.render_java_scripts()
        report['top_table'] = self.render_top_table(self.ordergroup, data)
        report['top_graph'] = self.url_graph(config['currentYear'], 'realisatie', model.ordergroup.encode(self.ordergroup_file, self.ordergroup.name))

        self.body = self.webrender.report(report)


    def create_bread_crums(self):
        groep = self.ordergroup
        bread_crum = [{'title': groep.descr, 'url': groep.name, 'class': 'active'}]
        while groep.parent:
            groep = groep.parent
            link = self.url(params={'ordergroep': self.ordergroup_file, 'subgroep': groep.name})
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
        tables = ['geboekt', 'obligo', 'plan']
        regels = model.regels.load(tables, years_load=self.years, orders_load=self.orders)
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

        # load data for all subgroups, including groups in subgroups
        ordergroups = self.ordergroup.list_groups()
        for group in ordergroups:
            data[group.name] = {}
            for year in self.years:
                data[group.name][year] = {}
                for tiepe in ['begroot', 'plan', 'resultaat', 'realisatie']:
                    data[group.name][year][tiepe] = 0

                    # add subgroup values
                    for subgroup in group.children:
                        if tiepe in data[subgroup.name][year]:
                            data[group.name][year][tiepe] += data[subgroup.name][year][tiepe]

                    # add orders from this grop
                    for order in group.orders:
                        if tiepe in data[order][year]:
                            data[group.name][year][tiepe] += data[order][year][tiepe]


                if data[group.name][year]['plan'] != 0:
                    data[group.name][year]['realisatie_perc'] = data[group.name][year]['realisatie'] / data[group.name][year]['plan'] * 100
                else:
                    data[group.name][year]['realisatie_perc'] = 0

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

    def render_fig(self):
        graphs = {}
        for year in reversed(self.years):
            graphs[year] = []
            # graphs of groups:
            for group in self.ordergroup.children:
                graph = {}
                graph['name'] = model.ordergroup.encode(self.ordergroup_file, group.name)
                graph['link'] = self.url(module='report', params={'ordergroup':(self.ordergroup_file), 'subgroup':group.name})
                graph['png'] = self.url_graph(year, 'realisatie', graph['name'])
                graphs[year].append(graph)

            # Graphs of orders
            for order, descr in self.ordergroup.orders.iteritems():
                graph = {}
                graph['link'] = self.url(module='view', params={'order':str(order)})
                graph['png'] = self.url_graph(year, 'realisatie', order)
                graphs[year].append(graph)

        figs = self.webrender.figpage(graphs, reversed(self.years))
        return figs

    def render_settings(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)

    def render_java_scripts(self):
        expand_items = []
        for child in self.ordergroup.children:
            expand_items.append(child.name)

        for year in self.years:
            expand_items.append(str(year))

        return self.webrender.javascripts(expand_items)

    def render_tables(self, data):
        tables = []
        if self.ordergroup.children:
            for ordergroep in self.ordergroup.children:
                if self.flat and ordergroep.children:
                    ordergroep = ordergroep.flat_copy()
                top_table = self.render_top_table(ordergroep, data)
                tables.append(top_table)

        return tables

    def render_top_table(self, ordergroup, data):
        header = {}
        header['name'] = ordergroup.descr
        header['link'] = self.url(params={'ordergroep': self.ordergroup_file, 'subgroep': ordergroup.name})
        header['id'] = ordergroup.name
        graph_name = model.ordergroup.encode(self.ordergroup_file, ordergroup.name)

        rows = []
        rows = self.group_to_rows(ordergroup, data)
        rows.extend(self.orders_to_rows(ordergroup, data))

        totals = data[ordergroup.name]
        for year in self.years:
            totals[year]['id'] = '%s-%s' % (year, ordergroup.name)
            graph_name = model.ordergroup.encode(self.ordergroup_file, ordergroup.name)
            totals[year]['graph'] = self.url_graph(year, 'realisatie', graph_name)

        top_table = self.webrender.table(self.years, rows, totals, header)
        return top_table

    def group_to_rows(self, ordergroup, data):
        group_rows = []
        for subgroup in ordergroup.children:
            row = {}
            row['link'] = self.url(params={'ordergroep': self.ordergroup_file, 'subgroep': subgroup.name})
            row['name'] = subgroup.descr
            row['order'] = None
            graph_name = model.ordergroup.encode(self.ordergroup_file, subgroup.name)
            row['id'] = subgroup.name

            for year in self.years:
                row[year] = {}
                row[year]['id'] = '%s-%s' % (year, subgroup.name)
                row[year]['graph'] = self.url_graph(year, 'realisatie', graph_name)
                row[year]['plan'] = data[subgroup.name][year]['plan']
                row[year]['realisatie'] = data[subgroup.name][year]['realisatie']
                row[year]['realisatie_perc'] = data[subgroup.name][year]['realisatie_perc']
                row[year]['resultaat'] = data[subgroup.name][year]['resultaat']
            group_rows.append(row)

        return group_rows

    def orders_to_rows(self, ordergroup, data):
        order_rows = []
        for order, descr in ordergroup.orders.iteritems():
            row = {}
            row['link'] = self.url(module='view', params={'order':order})
            row['name'] = descr
            row['order'] = order
            row['id'] = order

            for year in self.years:
                row[year] = {}
                row[year]['id'] = '%s-%s' % (year, order)
                row[year]['graph'] = self.url_graph(year, 'realisatie', order)
                row[year]['plan'] = data[order][year]['plan']
                row[year]['realisatie'] = data[order][year]['realisatie']
                row[year]['realisatie_perc'] = data[order][year]['realisatie_perc']
                row[year]['resultaat'] = data[order][year]['resultaat']
            order_rows.append(row)

        return order_rows

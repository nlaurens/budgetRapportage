from config import config
from controller import Controller
import web
from web import form

import numpy as np
import model.regels
import model.ksgroup
from functions import moneyfmt
from matplotlib import cm


class View(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'View'
        self.module = 'view'
        self.webrender = web.template.render('webpages/view/')

        # View specific:
        order = int(web.input(order=0)['order'])
        order_inst = model.orders.load(orders_load=[order]).orders
        if order_inst:
            self.order = order_inst[0]
        else:
            #TODO load empty order here!
            self.order = {}
            self.order.ordernummer = order
            self.order.ordernaam = 'inactive order'

        self.year = int(web.input(year=self.config["currentYear"])['year'])
        self.ksgroup_name = web.input(ksgroup_name=config['ksgroup']['default'])['ksgroup_name']
        self.periode = (web.input(periode='ALL')['periode'])
        subgroups = False
        if web.input().has_key('subgroups'):
            subgroups = True

        # Forms
        dropdown_options = self.dropdown_options()
        self.form_settings_simple = form.Form(
            form.Dropdown('year', dropdown_options['years'], value=self.year, class_="btn btn-default btn-sm"),
            form.Dropdown('periode', dropdown_options['periode_all'], value=self.periode, class_="btn btn-default btn-sm"),
            form.Dropdown('ksgroup_name', model.ksgroup.available(), value=self.ksgroup_name, class_="btn btn-default btn-sm"),
            form.Checkbox('subgroups', description='Show subgroups:', checked=subgroups),
            form.Button('Update', 'update', class_="btn btn-default btn-sm"),
        )

        # Load the ksgroup
        self.ksgroup_root = model.ksgroup.load(self.ksgroup_name)

        self.ksgroups = {}
        for batenlasten in ['baten', 'lasten']:
            self.ksgroups[batenlasten] = []
            for ksgroup_name in list(config['ksgroup']['ksgroups'][self.ksgroup_name][batenlasten]):
                ksgroup = self.ksgroup_root.find(ksgroup_name)
                if ksgroup.children:
                    if subgroups:
                        self.ksgroups[batenlasten].extend(ksgroup.get_end_children([]))
                    else:
                        for ksgroup in ksgroup.children:
                            self.ksgroups[batenlasten].append(ksgroup)
                else:
                    self.ksgroups[batenlasten].append(ksgroup)

    def authorized(self):
        if model.users.check_permission(['view']):
            ordernummer = self.order.ordernummer
            if self.order.ordernummer in model.users.orders_allowed():
                return True
        
        return False

    def process_sub(self):
        data, totals = self.construct_data()
        view = {}
        view['title'] = '%s - %s' % (self.order.ordernummer,self.order.ordernaam)
        view['summary'] = self.render_summary(totals)
        view['settings'] = self.render_settings()
        view['javaScripts'] = self.render_java_scripts(data)

        self.convert_data_to_str(data, totals)
        view['tables'] = self.render_tables(data, totals)
        self.body = self.webrender.view(view)
        return

    def construct_data(self):
        # data = { <name of ks_group>: { 'kosten/begroot': regellist}
        # totals {'geboekt/obligo/totals':<total>}

        regels = {}
        regels = model.regels.load(['geboekt', 'obligo'], years_load=[self.year], orders_load=[self.order.ordernummer], periods_load=self.periode)
        regels.extend(model.regels.load(['plan'], years_load=[self.year], orders_load=[self.order.ordernummer]))
        regels_dict = regels.split(['tiepe', 'kostensoort'])

        data = {}
        totals = {}
        totals['total'] = {}
        totals['total']['geboekt'] = 0
        totals['total']['obligo'] = 0
        totals['total']['plan'] = 0
        for batenlasten, ksgroups in self.ksgroups.iteritems():
            for ksgroup in ksgroups:
                for ks, descr in ksgroup.get_ks_recursive().items():
                    for tiepe in ['geboekt', 'obligo', 'plan']:
                        if tiepe in regels_dict:
                            if ks in regels_dict[tiepe]:
                                if ksgroup.name not in totals:
                                    totals[ksgroup.name] = {}
                                    totals[ksgroup.name]['geboekt'] = 0
                                    totals[ksgroup.name]['obligo'] = 0
                                    totals[ksgroup.name]['plan'] = 0

                                    data[ksgroup.name] = {}
                                    data[ksgroup.name]['kosten'] = None
                                    data[ksgroup.name]['begroot'] = None

                                key = ('kosten', 'begroot')[tiepe=='plan']
                                if data[ksgroup.name][key] is None:
                                    data[ksgroup.name][key] = regels_dict[tiepe][ks]
                                else:
                                    data[ksgroup.name][key].extend(regels_dict[tiepe][ks])

                                totals[ksgroup.name][tiepe] += regels_dict[tiepe][ks].total()
                                totals['total'][tiepe] += regels_dict[tiepe][ks].total()


        # sort regels in regellist by 'periode' for view:
        for ks_group in data.keys():
            for key in data[ks_group]:
                if data[ks_group][key] is not None:
                    data[ks_group][key].sort('periode')

        return data, totals

    def render_tables(self, data, totals):
        tables = []
        for batenlasten, ksgroups in self.ksgroups.iteritems():
            for ksgroup in ksgroups:
                if ksgroup.name in data:
                    header = {}
                    header['descr'] = ksgroup.descr
                    header['name'] = ksgroup.name
                    header['id'] = hash(ksgroup.name)

                    regels = []
                    if data[ksgroup.name]['kosten'] is not None:
                        regels = data[ksgroup.name]['kosten'].regels

                    table = self.webrender.table(regels, header, totals)
                    tables.append(table)

        return tables

    def convert_data_to_str(self, data, totals):
        for ks_group, data_dict in data.iteritems():
            for tiepe, regels in data_dict.iteritems():
                if regels is not None:
                    for regel in regels.regels:
                        regel.kosten = moneyfmt(regel.kosten)

        for ks_group, data_dict in totals.iteritems():
            for tiepe, total in data_dict.iteritems():
                totals[ks_group][tiepe] = moneyfmt(total)

        return data, totals

    def render_summary(self, totals):
        summary = {}

        summary['begroting'] = totals['total']['plan']

        summary['baten'] = 0
        for ksgroup in self.ksgroups['baten']:
            if ksgroup.name in totals:
                summary['baten'] = summary['baten'] + totals[ksgroup.name]['geboekt']

        summary['lasten'] = totals['total']['geboekt'] - summary['baten']
        summary['obligo'] = totals['total']['obligo'] - summary['baten']
        summary['ruimte'] = summary['begroting'] - summary['baten'] - summary['lasten']
        for key in summary.keys():
            summary[key] = moneyfmt(summary[key])


        summary['bh'] = self.order.budgethouder
        summary['subact'] = self.order.subactiviteitencode

        summary['graph_realisatie'] = self.url_graph(self.year, 'realisatie', self.order.ordernummer)

        return self.webrender.summary(summary)

    def render_settings(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)


    def render_java_scripts(self, data):
        expand_items = []
        for ks_group in data.keys():
            expand_items.append(hash(ks_group))

        return self.webrender.javascripts(expand_items)

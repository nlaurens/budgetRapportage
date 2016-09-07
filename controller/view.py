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
#TODO to config params
        self.order = int(web.input(order=2008502040)['order'])
        self.maxdepth = int(web.input(maxdepth=1)['maxdepth'])
        self.KSgroep = int(web.input(ksgroep=0)['ksgroep'])
        self.year = int(web.input(jaar=self.config["currentYear"])['jaar'])
        self.periode = int(web.input(periode=0)['periode'])
        self.clean = web.input().has_key('clean')

        # Forms
# TODO dropdowns!
        self.form_settings_simple = form.Form(
#TODO use config params and years form model
            form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')], class_="btn btn-default btn-sm"),
            form.Dropdown('periode', [(0, 'All'), (1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')], class_="btn btn-default btn-sm"),
            form.Dropdown('ksgroep', []),
            form.Button('Update', 'update', class_="btn btn-default btn-sm"),
        )

#TODO this is copied from graph.py. Double code, refactor! Perhaps do the mapping in model.ksgroups?
# and load the color scheme from config.
# It really feels like we made the model.budget.ksgroup object redundant with the regellist and ksgroup hashmap
        ksgroup_root = model.ksgroup.load(config['graphs']['ksgroup'])
        ks_map = {}
        color_map = {'baten': {}, 'lasten': {}}
        for tiepe in ['baten', 'lasten']:
            for child in ksgroup_root.find(config['graphs'][tiepe]).children:
                color_map[tiepe][child.descr] = {}
                for ks in child.get_ks_recursive():
                    ks_map[ks] = (tiepe, child.descr)

            colors_amount = max(len(color_map[tiepe]), 3)  # prevent white colors
            colors = {}
            colors['baten'] = cm.BuPu(np.linspace(0.75, 0.1, colors_amount))
            colors['lasten'] =cm.BuGn(np.linspace(0.75, 0.1, colors_amount))
            for i, key in enumerate(color_map[tiepe]):
                color_map[tiepe][key] = colors[tiepe][i]

        self.color_map = color_map
        self.ks_map = ks_map

    def process_sub(self):
        data, totals = self.construct_data()
        view = {}
        view['title'] = model.orders.get_name(self.order) + ' ' + str(self.order)
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
        regels = model.regels.load(years_load=[self.year], orders_load=[self.order])

        #TODO self.periodes in init
        self.periodes = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        regels.filter_regels_by_attribute('periode', self.periodes)

        regels_dict = regels.split(['kostensoort', 'tiepe'])

        totals = {}
        totals['total'] = {}
        totals['total']['geboekt'] = 0
        totals['total']['obligo'] = 0
        totals['total']['plan'] = 0

        data = {}
        for ks, regels_tiepe in regels_dict.iteritems():
            ks_group = self.ks_map[ks][1]

            if ks_group not in totals:
                totals[ks_group] = {}
                totals[ks_group]['geboekt'] = 0
                totals[ks_group]['obligo'] = 0
                totals[ks_group]['plan'] = 0

                data[ks_group] = {}
                data[ks_group]['kosten'] = None
                data[ks_group]['begroot'] = None

            for tiepe in ['geboekt', 'obligo']:
                if tiepe in regels_tiepe:
                    if data[ks_group]['kosten'] is None:
                        data[ks_group]['kosten'] = regels_tiepe[tiepe]
                    else:
                        data[ks_group]['kosten'].extend(regels_tiepe[tiepe])

                    totals[ks_group][tiepe] += regels_tiepe[tiepe].total()
                    totals['total'][tiepe] += regels_tiepe[tiepe].total()

            if 'plan' in regels_tiepe:
                if data[ks_group]['begroot'] is None:
                    data[ks_group]['begroot'] = regels_tiepe['plan']
                else:
                    data[ks_group]['begroot'].extend(regels_tiepe['plan'])

        # sort regels in regellist by 'periode' for view:
        for ks_group in data.keys():
            for key in data[ks_group]:
                if data[ks_group][key] is not None:
                    data[ks_group][key].sort('periode')

        return data, totals

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
        import pprint
        pprint.pprint(totals)
        summary = {}
        summary['begroting'] = totals['total']['plan']
        if 'Baten' in totals:
            summary['baten'] = totals['Baten']['geboekt'] + totals['Baten']['obligo']
        else:
            summary['baten'] = 0

        summary['lasten'] = totals['total']['geboekt'] + totals['total']['obligo'] - summary['baten']
        summary['ruimte'] = summary['begroting'] - summary['baten'] - summary['lasten']

        for key in summary.keys():
            summary[key]  = moneyfmt(summary[key])

        return self.webrender.summary(summary)

    def render_settings(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)

    def render_tables(self, data, totals):
        tables = []
        for ks_group, regels in data.iteritems():
            header = {}
            header['name'] = ks_group
            header['id'] = hash(ks_group)

            print regels
            if regels['kosten'] is not None:
                regels = regels['kosten'].regels
            else:
                regels = []

            table = self.webrender.table(regels, header, totals)
            tables.append(table)

        return tables

    def render_java_scripts(self, data):
        expand_items = []
        for ks_group in data.keys():
            expand_items.append(hash(ks_group))

        return self.webrender.javascripts(expand_items)

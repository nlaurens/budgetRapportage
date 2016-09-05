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

        data = self.construct_data()
        self.convert_data_to_str(data)

        view = {}
        view['title'] = model.orders.get_name(self.order) + ' ' + str(self.order)
        view['summary'] = self.render_summary(data)
        view['settings'] = self.render_settings()
        view['tables'] = self.render_tables(data)
        self.body = self.webrender.view(view)
        return

    def construct_data(self):
        regels = {}
        regels = model.regels.load(years_load=[self.year], orders_load=[self.order])
        
        #TODO self.periodes in init
        self.periodes = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
        regels.filter_regels_by_attribute('periode', self.periodes)

        regels_dict = regels.split(['tiepe', 'kostensoort'])

        data = {}
        for tiepe, regels_ks in regels_dict.iteritems():
            data[tiepe] = {}
            for ks, regels in regels_ks.iteritems():
                ks_group = self.ks_map[ks]
                if ks_group not in data[tiepe]:
                    data[tiepe][ks_group] = regels
                else:
                    data[tiepe][ks_group].extend(regels)

        # sort new regellist and 
        for tiepe in data.keys():
            print tiepe
            totals = {}
            totals['total'] = 0

            for ks_group, regels in data[tiepe].iteritems():
                regels.sort_by_attribute('periode')

                totals[ks_group] = regels.total()
                totals['total'] += totals[ks_group]

            data[tiepe]['totals'] = totals

        # BUILD regellist per ksgroup in de self.ksmap and create totals 'baten', 'lasten', 'plan'. 

        # data['baten'/'lasten/plan']['ksgroup']['ks'] = regellist

        # data['baten'/'lasten/plan']['ksgroup']['ks'][totals] = float
        # data['baten'/'lasten/plan']['ksgroup'][totals] = float
        # data['baten'/'lasten/plan'][totals] = float

        return data

    def convert_data_to_str(self, data):
        return data

    def render_summary(self, data):
        summary = {}
        summary['begroting'] = 100
        summary['baten'] = 50
        summary['lasten'] = 50
        summary['ruimte'] = 50
        return self.webrender.summary(summary)

    def render_settings(self):
        form_settings = self.form_settings_simple
        return self.webrender.settings(form_settings)

    def render_tables(self, data):
        return ['dummy 1', 'dummy2']
# TODO settings forms invullen
        # KSgroepen = model.loadKSgroepen()
        # fill_dropdowns(form, settings, KSgroepen)

        regels = model.regels.load(years_load=[self.jaar], orders_load=[self.order])
# TODO replace with param/CONFIG
        ksgroup = model.ksgroup.load('WNMODEL4')
        ksgroup.assign_regels_recursive(regels)
        ksgroup.set_totals()
# TODO replace with param
        root_baten = ksgroup.find('WNTBA')
        root_lasten = ksgroup.find('WNTL')

        if self.clean:
            root_baten.clean_empty_nodes()
            root_lasten.clean_empty_nodes()

        totaal = {}
        totaal['order'] = self.order
        totaal['begroting'] = ksgroup.totaalTree['plan']
        totaal['baten'] = root_baten.totaalTree['geboekt'] + root_baten.totaalTree['obligo']
        totaal['lasten'] = root_lasten.totaalTree['geboekt'] + root_lasten.totaalTree['obligo']

        # TODO implment reserves
        totaal['reserve'] = 0

        if totaal['reserve'] < 0:
            totaal['ruimte'] = -1*(ksgroup.totaalTree['geboekt'] + ksgroup.totaalTree['obligo']) + totaal['begroting'] + totaal['reserve']
        else:
            totaal['ruimte'] = -1*(ksgroup.totaalTree['geboekt'] + ksgroup.totaalTree['obligo']) + totaal['begroting']

        totaal['reserve'] = moneyfmt(totaal['reserve'])
        totaal['ruimte'] = moneyfmt(totaal['ruimte'])
        totaal['baten'] = moneyfmt(totaal['baten'])
        totaal['lasten'] = moneyfmt(totaal['lasten'])
        totaal['begroting'] = moneyfmt(totaal['begroting'])

        htmlgrootboek = []
        for child in ksgroup.children:
            htmlgrootboek.append(self.html_tree(child, 0))

        self.body = self.webrender.view(self.settings_simple_form, 'dummy sap datum', htmlgrootboek, totaal)

    def html_tree(self, root, depth):
        depth += 1

        groups = []
        for child in root.children:
            groups.append(self.html_tree(child, depth))

        unfolded = False  # Never show the details

        regelshtml = []
        totals_node = {}  #Always initialize all to 0 to prevent render problems
        totals_node['geboekt'] = root.totaalTree['geboekt']
        totals_node['obligo'] = root.totaalTree['obligo']
        totals_node['plan'] = root.totaalTree['plan']

# TODO import should be moving
        from model.budget import RegelList
        regels_per_ks_per_tiepe = RegelList()  # Create 1 regellist and not a dict per type
        for key, regelsPerTiepe in root.regels.iteritems():
            regels_per_ks_per_tiepe.extend(regelsPerTiepe)

        regels_per_ks_per_tiepe = regels_per_ks_per_tiepe.split(['kostensoort', 'tiepe'])
        for kostenSoort, regelsPerTiepe in regels_per_ks_per_tiepe.iteritems():

# TODO Already in kostensoortgroup!
            totals_ks = {}
            totals_ks['geboekt'] = 0
            totals_ks['obligo'] = 0
            totals_ks['plan'] = 0
            for tiepe, regellist in regelsPerTiepe.iteritems():
                totals_ks[tiepe] = regellist.total()

                for regel in regellist.regels:
                    regel.kosten = moneyfmt(regel.kosten, places=2, dp='.')

                ks_name = root.kostenSoorten[kostenSoort]
                ks_name = str(kostenSoort) + ' - ' + ks_name.decode('ascii', 'replace').encode('utf-8')
                regelshtml.append(self.webrender.regels(root.name, kostenSoort, ks_name, totals_ks, regellist.regels, unfolded))

        if depth <= self.maxdepth:
            unfolded = True
        else:
            unfolded = False

        for key, amount in totals_node.iteritems():
            totals_node[key] = moneyfmt(amount, places=2, dp='.')

        return self.webrender.grootboekgroep(root.name, root.descr, groups, regelshtml, unfolded, totals_node, depth)

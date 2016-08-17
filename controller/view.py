from functions import moneyfmt
from controller import Controller
import web
from web import form

import model.regels
import model.ksgroup


class View(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'View'
        self.module = 'view'
        self.webrender = web.template.render('webpages/view/')

        # View specific:
        self.order = int(web.input(order=2008502040)['order'])
        self.maxdepth = int(web.input(maxdepth=1)['maxdepth'])
        self.KSgroep = int(web.input(ksgroep=0)['ksgroep'])
        self.jaar = int(web.input(jaar=self.config["currentYear"])['jaar'])
        self.periode = int(web.input(periode=0)['periode'])
        self.clean = web.input().has_key('clean')

        # Forms
# TODO dropdowns!
        self.settings_simple_form = form.Form(
            form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')], class_="btn btn-default btn-sm"),
            form.Dropdown('periode', [(0, 'All'), (1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')], class_="btn btn-default btn-sm"),
            form.Hidden('maxdepth', [(0, '1. Totals'), (1, '2. Subtotals'), (10, '3. Details')]),
            form.Hidden('ksgroep', []),
            form.Hidden('clean'),
            form.Button('Update', 'update', class_="btn btn-default btn-sm"),
        )
        self.settings_expert_form = form.Form(
            form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')]),
            form.Dropdown('periode', [('', 'all')]),
            form.Dropdown('maxdepth', [(0, '1. Totals'), (1, '2. Subtotals'), (10, '3. Details')]),
            form.Dropdown('ksgroep', []),
            form.Checkbox('clean'),
            form.Button('Update', 'update'),
        )

    def process_sub(self):
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

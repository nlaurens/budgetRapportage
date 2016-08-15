from functions import moneyfmt
from controller import Controller
import web
from web import form
import model.db
import budget

class View(Controller):
    def __init__(self):
        Controller.__init__(self)

        #subclass specific
        self.title = 'View'
        self.module = 'view'
        self.webrender = web.template.render('webpages/view/')

        #View specific:
        self.order = int(web.input(order=2008502040)['order'])
        self.maxdepth = int(web.input(maxdepth=1)['maxdepth'])
        self.KSgroep = int(web.input(ksgroep=0)['ksgroep'])
        self.jaar = int(web.input(jaar=self.config["currentYear"])['jaar'])
        self.periode = int(web.input(periode=0)['periode'])
        self.clean = web.input().has_key('clean')

        #Forms
#TODO dropdowns!
        self.settings_simple_form = form.Form(
            form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')], class_="btn btn-default btn-sm"),
            form.Dropdown('periode', [(0, 'All'), (1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')], class_="btn btn-default btn-sm"),
            form.Hidden('maxdepth', [(0,'1. Totals'), (1,'2. Subtotals'), (10, '3. Details')]),
            form.Hidden('ksgroep', []),
            form.Hidden('clean'),
            form.Button('Update', 'update', class_="btn btn-default btn-sm"),
        )
        self.settings_expert_form = form.Form(
            form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')]),
            form.Dropdown('periode', [('', 'all')]),
            form.Dropdown('maxdepth', [(0,'1. Totals'), (1,'2. Subtotals'), (10, '3. Details')]),
            form.Dropdown('ksgroep', []),
            form.Checkbox('clean'),
            form.Button('Update', 'update'),
        )

    def process_sub(self):
#TODO settings forms invullen
        #KSgroepen = model.loadKSgroepen()
        #fill_dropdowns(form, settings, KSgroepen)

        regels = model.db.get_regellist_per_table(jaar=[self.jaar], orders=[self.order])
#TODO replace with param/CONFIG
        og = model.db.loadKSgroepen()['WNMODEL4']
        root = budget.grootboek.load(og)
        root.assign_regels_recursive(regels)
        root.set_totals()
#TODO replace with param
        rootBaten = root.find('WNTBA')
        rootLasten = root.find('WNTL')

        if self.clean:
            rootBaten.clean_empty_nodes()
            rootLasten.clean_empty_nodes()

        totaal = {}
        totaal['order'] = self.order
        totaal['begroting'] = root.totaalTree['plan']
        totaal['baten'] = rootBaten.totaalTree['geboekt'] + rootBaten.totaalTree['obligo']
        totaal['lasten'] = rootLasten.totaalTree['geboekt'] + rootLasten.totaalTree['obligo']

        reserves = model.db.get_reserves()
        try:
            totaal['reserve'] = reserves[str(self.order)]
        except:
            totaal['reserve'] = 0

        if totaal['reserve'] < 0:
            totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting'] + totaal['reserve']
        else:
            totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting']

        totaal['reserve'] = moneyfmt(totaal['reserve'])
        totaal['ruimte'] = moneyfmt(totaal['ruimte'])
        totaal['baten'] = moneyfmt(totaal['baten'])
        totaal['lasten'] = moneyfmt(totaal['lasten'])
        totaal['begroting'] = moneyfmt(totaal['begroting'])

        htmlgrootboek = []
        for child in root.children:
            htmlgrootboek.append(self.html_tree(child, 0))

        self.body = self.webrender.view(self.settings_simple_form, 'dummy sap datum', htmlgrootboek, totaal)


    def html_tree(self, root, depth):
        depth += 1

        groups = []
        for child in root.children:
            groups.append(self.html_tree(child, depth))

        unfolded = False # Never show the details

        regelshtml = []
        totalsNode = {} #Always initialize all to 0 to prevent render problems
        totalsNode['geboekt'] = root.totaalTree['geboekt']
        totalsNode['obligo'] = root.totaalTree['obligo']
        totalsNode['plan'] = root.totaalTree['plan']

        regelsPerKSPerTiepe = budget.RegelList() # Create 1 regellist and not a dict per type
        for key, regelsPerTiepe in root.regels.iteritems():
            regelsPerKSPerTiepe.extend(regelsPerTiepe)

        regelsPerKSPerTiepe = regelsPerKSPerTiepe.split_by_regel_attributes(['kostensoort','tiepe'])
        for kostenSoort, regelsPerTiepe in regelsPerKSPerTiepe.iteritems():
            totalsKS = {}
            totalsKS['geboekt'] = 0
            totalsKS['obligo'] = 0
            totalsKS['plan'] = 0
            for tiepe, regellist in regelsPerTiepe.iteritems():
                totalsKS[tiepe] = regellist.total()

                for regel in regellist.regels:
                    regel.kosten = moneyfmt(regel.kosten, places=2, dp='.')

                KSname = root.kostenSoorten[kostenSoort]
                KSname = str(kostenSoort) +' - ' + KSname.decode('ascii', 'replace').encode('utf-8')
                regelshtml.append(self.webrender.regels(root.name, kostenSoort, KSname, totalsKS, regellist.regels, unfolded))

        if depth <= self.maxdepth:
            unfolded = True
        else:
            unfolded = False

        for key, amount in totalsNode.iteritems():
            totalsNode[key] = moneyfmt(amount, places=2, dp='.')

        return self.webrender.grootboekgroep(root.name, root.descr, groups, regelshtml, unfolded, totalsNode, depth)

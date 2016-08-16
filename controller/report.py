from controller import Controller
import web
from web import form
import numpy as np

class Report(Controller):
    def __init__(self):
        Controller.__init__(self)

        #subclass specific
        self.title = 'Report'
        self.module = 'report'
        self.webrender = web.template.render('webpages/report/', cache=False)

        #Salaris specific:
        #Report specific:
        self.jaar = int(web.input(jaar=self.config["currentYear"])['jaar'])
#TODO config
        self.subgroep = str(web.input(subgroep='TOTAAL')['subgroep'])
        self.ordergroep = str(web.input(ordergroep='LION')['ordergroep'])
        self.flat = bool(int(web.input(flat='0')['flat']))
        self.expandOrders = bool(int(web.input(expandOrders='0')['expandOrders']))
        self.regels = {} #Dictionary per order, per tiepe = regellist
        self.orders = [] #list of all orders in the group

    def process_sub(self):
        ogPath = model.db.loadOrderGroepen()[self.ordergroep]
        orderGroep = budget.ordergroep.load(ogPath)
        orderGroep = orderGroep.find(self.subgroep) #AIAI!
        if self.flat:
            orderGroep = orderGroep.flat_copy()

        self.root = orderGroep

        #construct beadcrumbs
        groep = self.root
        breadCrum = [ {'title':groep.descr, 'url':groep.name, 'class':'active'}]
        while groep.parent:
            groep = groep.parent
            link = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroep, groep.name)
            breadCrum.append({'title':groep.descr, 'url':link, 'class':''})

        self.breadCrum = reversed(breadCrum)

        self.orders = self.root.list_orders_recursive().keys()
        regels = model.db.get_regellist(jaar=[self.jaar], orders=self.orders)
        self.regels = regels.split_by_regel_attributes(['ordernummer', 'tiepe'])

#TODO lijkt erop dat dit recursie is die we in de render_body all kunnen doen
        body = self.render_table_html()
        figs = self.render_fig_html()
        settings = self.render_settings_html()
        javaScripts = self.render_java_scripts()

        report = {}
        report['settings'] = settings
        report['figpage'] = figs
        report['nav'] = ' DUMMy'
        report['body'] = body
        report['javaScripts'] = javaScripts

        self.body = self.webrender.report(report)

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
            childtable.append(self.webrender.table_groep(rows, header, groeprows))
            groeptotal['begroot'] += total['begroot']
            groeptotal['realisatie'] += total['realisatie']
            groeptotal['obligo'] += total['obligo']
            groeptotal['resultaat'] += total['resultaat']

        #add orders of the top group (if any)
        order_tables, header,total = self.parse_orders_in_groep(self.root, groeptotal)
        table.append(self.webrender.table_groep(order_tables, header, childtable))

        body = self.webrender.table(table)
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
            groeprows.append(self.webrender.table_groep(childOrderTables, childheader, childgroep))
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
            order_table, totaalTree = self.parse_order(order, descr)
            order_tables.append(order_table)
            total_groep['begroot'] += totaalTree['plan']
            total_groep['realisatie'] += totaalTree['geboekt'] + totaalTree['obligo']
            total_groep['resultaat'] += totaalTree['plan'] - totaalTree['geboekt'] - totaalTree['obligo']

        groep_header = {}
        groep_header['row'] = self.groep_regel_to_html(total_groep)
        groep_header['id'] = root.name
        groep_header['img'] = self.url_graph(self.jaar, 'realisatie', root.name)

        return order_tables, groep_header, total_groep


    def parse_order(self, order, descr):
        #parse orders in groep:
        regels = {}
        if order in self.regels:
            regels = self.regels[order]

#TODO  In config params!!
        ksPath = model.db.loadKSgroepen()['BFRE15']
        root = budget.grootboek.load(ksPath)
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
        header['name'] = '%s (%s)' % (descr, order)
        header['link'] = '/view/%s?order=%s' % (self.userHash, order)
        header['userHash'] = self.userHash
        header['id'] = order
        header['img'] = self.url_graph(self.jaar, 'realisatie', order)
        header['begroot'] = table_string(root.totaalTree['plan'])
        header['realisatie'] =  table_string(root.totaalTree['geboekt'] + root.totaalTree['obligo'])
        header['resultaat'] = table_string(root.totaalTree['plan'] - root.totaalTree['geboekt'] - root.totaalTree['obligo'])

        order_table = self.webrender.table_order(html_rows, header, self.expandOrders)
        return order_table, root.totaalTree


    def grootboek_regel_to_html(self, row):
        html = row.copy()
        html['grootboek'] = row['grootboek']
        html['begroot'] = table_string(row['begroot'])
        html['realisatie'] =  table_string(row['realisatie'])
        html['resultaat'] = table_string(row['resultaat'])
        return self.webrender.table_grootboek_regel(html)


    def groep_regel_to_html(self, row):
        html = row.copy()
        html['name'] = row['name'] 
        html['link'] = '%s?ordergroep=%s&subgroep=%s' % (self.url(), self.ordergroep, row['id'] )
        html['begroot'] = table_string(row['begroot'])
        html['realisatie'] =  table_string(row['realisatie'])
        html['resultaat'] = table_string(row['resultaat'])
        return self.webrender.table_groep_regel(html)


#TODO layout!
    def render_fig_html(self):
        figs = ''
        if not self.root.children:
            graphs = []
            i = 0
            for order, descr in self.root.orders.iteritems():
                graph = {}
                graph['link'] = ('../view/' + self.userHash + '/' + str(order))
                graph['png'] = self.url_graph(self.jaar, 'realisatie', order)
                #if i%2:
                #    graph['spacer'] = '</tr><tr>'
                #else:
                #    graph['spacer'] = ''
                graphs.append(graph)
                i +=1

            figs = self.webrender.figpage(graphs)
            return figs
        else:
            return None

#TODO replace dummy vasr
    def render_settings_html(self):
        form = 'FORM met daarin jaar'
        buttons = 'BUTTON'
        lastupdate = '2'
        return self.webrender.settings(lastupdate, buttons, form)

    def render_java_scripts(self):
        expandItems = self.orders
        expandItems.extend(self.root.list_groepen_recursive().values())
        print expandItems
        print type(expandItems)
        return self.webrender.javascripts(expandItems)


###########################################################
#Functions
###########################################################
#TODO dit naar functions zodat er 1 functie voor is (graph.py heeft het ook al d8 ik)
def table_string(value):
    value = value/1000
    if value == 0 or np.abs(value) < 0.5:
        return '&nbsp;'
    else:
        return ('%.f' % value)


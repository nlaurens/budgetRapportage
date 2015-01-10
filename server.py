""""
TODO
 - maxdepth uit de GET_Vars halen en linkje in settings maken voor:
   alles uitklappen, alles inklappen.

 - Summary uitwerken: reserve, totalen baten, totalen kosten.

 - Wildcards voor ordernummer range in authorisatie lijst inbouwen
   (bv 2868*). Refactor de userHash gedeelte in server.py naar functie.

 - model.getObligo / .geGeboekt ipv 1 kostenSoort
    een lijst van KostenSoorten geven die in 1 MYSQL query gaat
    NU doe ik 10 voor dezelfde order, dat zou ook bij elkaar moeten kunnen.
    omdat we nu uitgaan van grootboek ipv ordernummers..

- Show negative bestedingsruimte in red and bold.


"""
import web
import model
import GrootBoek
from config import config
from functions import moneyfmt
from decimal import *


class Index:
    def __init__(self):
        pass

    @staticmethod
    def GET():
        return render.index()


class Overview:
    def __init__(self):
        pass

    @staticmethod
    def GET(userHash):
        if userHash == '':
            return web.notfound("Sorry the page you were looking for was not found.")

        budgets = model.get_budgets(userHash, config["salt"])
        if not budgets:
            return web.notfound("Sorry the page you were looking for was not found.")

        if budgets[0] == "*":
            budgets = model.get_orders()

        maxdepth = 1
        grootboek = 'data/kostensoortgroep/28totaal4.txt'
        sapdatum = '25-5-2014'
        reserves = model.get_reserves()

        headers = ['Order', 'Stand op 1 jan', 'Bestedingsruimte']

        headersgrootboek = {}
        root = GrootBoek.load(0, grootboek)
        for child in root.children:
            headersgrootboek[child.name] = child.descr

        orders = []
        for order in budgets:
            line = {}
            root = GrootBoek.load(order, grootboek)
            line['order'] = order
            line['reserve'] = Decimal(reserves[str(order)])
            if line['reserve'] < 0:
                line['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + line['reserve']
            else:
                line['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree)

            for child in root.children:
                line[child.name] = moneyfmt((-1*(child.totaalGeboektTree + child.totaalObligosTree)))

            line['reserve'] = moneyfmt(line['reserve'])
            line['ruimte'] = moneyfmt(line['ruimte'])
            orders.append(line)

        return render.overview(headers, headersgrootboek, orders, sapdatum, grootboek, userHash)


class View:
    def __init__(self):
        pass

    @staticmethod
    def GET(userHash, order):

        if userHash == '':
            return web.notfound("Sorry the page you were looking for was not found.")

        budgets = model.get_budgets(userHash, config["salt"])
        if not budgets:
            return web.notfound("Sorry the page you were looking for was not found.")

        if budgets[0] != "*" and order not in budgets:
            return web.notfound("Sorry the page you were looking for was not found.")

        order = int(order)
        maxdepth = 5
        grootboek = 'data/kostensoortgroep/28totaal4.txt'
        sapdatum = '25-5-2014'
        root = GrootBoek.load(order, grootboek)
        reserves = model.get_reserves()
        totaal = {}
        htmlgrootboek = []

        for child in root.children:
            htmlgrootboek.append(child.html_tree(render, maxdepth, 0))
            if child.name == '28BATENTEX':
                totaal['baten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))
            elif child.name == '28LASTEN-T':
                totaal['lasten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))
            elif child.name == '28LASTENOL':
                totaal['lasten'] += (-1*(child.totaalGeboektTree + child.totaalObligosTree))

        totaal['order'] = order
        totaal['reserve'] = Decimal(reserves[str(order)])
        if totaal['reserve'] < 0:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['reserve']
        else:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree)

        totaal['reserve'] = moneyfmt(totaal['reserve'])
        totaal['ruimte'] = moneyfmt(totaal['ruimte'])
        totaal['baten'] = moneyfmt(totaal['baten'])
        totaal['lasten'] = moneyfmt(totaal['lasten'])
        return render.view(grootboek, sapdatum, htmlgrootboek, totaal)


### Url mappings
urls = (
    '/', 'Index',
    '/overview/(.+)', 'Overview',
    '/view/(.+)/(\d+)', 'View',
)

### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates/')

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

""""
BUGS

  - Baten verdwijnen
  - SQL inject in model bekijken

        REINTRODUCE SECURITY:
        if not webaccess.check_auth(session, userHash, 'graph'):
            return web.notfound("Sorry the page you were looking for was not found.")
TODO

- test om forms uit functies te halen en in de classe zelf te zetten (los). of los onderaan. Werkt dat met params?
- params uit de Webpage verwijderen (self.params <- in form zitten ze al en get apart parsen in de server class)

- add checking if user is allowed for the order he is viewing. Right now we don't use thge auth file other to see if you can login or not.

- redirect to requrested page after login

- webaccess only checks IP access not if the budget# is allowed for that user

- 'prognose' posten toevoegen.
- verplaats alle decode/encode naar model (db_2_regel)

- Het kan zijn dat er begroting is op een KS die niet geboekt is. Dan komt hij NIET in het overzicht. FIXEN!

- Importeer functie maken die vraagt om welke kolom wat bevat (namen zijn strings die iedereen apart instelt in SAP....)

 - 'AFREKORD' grootboek weer toevoegen alleen als hij ook bestaat voor die orders.

 - kpl support toevoegen

 - WBS support toevoegen (betekend lijst maken met welk wbs bij welke groep hoort..)

- Show negative bestedingsruimte in red and bold.

 - ik bedacht me later dat het misschien een goed idee is om boven alle tabbladen de boodschap te zetten in boldface:
Notice that these records show only transactions up to (datum van laatste update)

- Rewrite templates to be more modular with css and header parts:
    http://webpy.org/cookbook/layout_template

Somday/Maybe:

#cool d3 ding:
- http://bl.ocks.org/NPashaP/96447623ef4d342ee09b
"""
# TIP: render.<template>(arg1, arg2, arg3, cache=False) will reload the template file everytime you refresh
import web
web.config.debug = True #Set to False for no ouput! Must be done before the rest
import model
import GrootBoek
import OrderGroep
import os
from config import config

# web-pages
import webpage #mother class and simple page
import webindex
import webaccess
import webadmin

#web utilies
import webgraph


class Index:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'index')

        page = webpage.Simple(userHash, 'Welcome', 'Make a selection from the menu above.')
        return page.render()


class Admin:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'admin')
        page = webadmin.Admin(userHash)
        return page.render()

    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'admin')
        page = webadmin.Admin(userHash, 'formAction')
        return page.render()


class Login:
    def GET(self, userHash):
        auth_block_by_ip()
        page = webaccess.Login(userHash)
        return page.render()

    def POST(self, userHash):
        auth_block_by_ip()
        page = webaccess.Login(userHash)
        page.parse_form(session) #will redirect on success
        return page.render()


class Logout:
    def GET(self, userHash):
        auth_block_by_ip()
        session.logged_in = False
        page = webpage.Simple(userHash, 'Logout', 'You have been logged out')
        return page.render()


class Graph:
    def GET(self, userHash, jaar, tiepe, order):
        auth_block_by_ip()
        auth_login(session, userHash, 'index')
        return webgraph.return_graph(jaar, tiepe, order)


#TODO convert to webpage class
class View:
    settings_simple_form = web.form.Form(
        web.form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')], class_="btn btn-default btn-sm"),
        web.form.Dropdown('periode', [(0, 'All'), (1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')], class_="btn btn-default btn-sm"),
        web.form.Hidden('maxdepth', [(0,'1. Totals'), (1,'2. Subtotals'), (10, '3. Details')]),
        web.form.Hidden('ksgroep', []),
        web.form.Hidden('clean'),
        web.form.Button('Update', 'update', class_="btn btn-default btn-sm"),
    )
    settings_expert_form = web.form.Form(
        web.form.Dropdown('jaar', [(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')]),
        web.form.Dropdown('periode', [('', 'all')]),
        web.form.Dropdown('maxdepth', [(0,'1. Totals'), (1,'2. Subtotals'), (10, '3. Details')]),
        web.form.Dropdown('ksgroep', []),
        web.form.Checkbox('clean'),
        web.form.Button('Update', 'update'),
    )
    def __init__(self):
        pass


    def get_post_params(self, form):
        try:
            maxdepth = int(web.input()['maxdepth'])
        except:
            maxdepth = 1

        try:
            KSgroep = int(web.input()['ksgroep'])
        except:
            KSgroep = 0

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = config["currentYear"]

        try:
            periode = int(web.input()['periode'])
        except:
            periode = 0

        clean = web.input().has_key('clean')

        return {"maxdepth":maxdepth, "KSgroep":KSgroep, "jaar":jaar, "periode":periode, "clean":clean}

    def POST(self, userHash, order):
        form = self.settings_simple_form
        if not webaccess.check_auth(session, userHash, 'view'):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        return webview.view(settings, render, form, order)

    def GET(self, userHash, order):
        form = self.settings_simple_form
        if not webaccess.check_auth(session, userHash, 'view'):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        settings["clean"] = True
        return webview.view(settings, render, form, order)

#TODO convert to webpage class
class Report:
    def get_params(self):

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = config["currentYear"]

        try:
            periode = web.input()['periode']
        except:
            periode = '0,1,2,3,4,5,6,7,8,9,10,11,12'

        try:
            groep = web.input()['groep']
        except:
            groep = 'TOTAAL'

        return jaar, periode, groep

    def POST(self, userHash):
        return None

    def GET(self, userHash):
        if not webaccess.check_auth(session, userHash, 'report'):
            return web.notfound("Sorry the page you were looking for was not found.")
        jaar, periode, groep = self.get_params()
        report = webreport.groep_report(userHash, render, groep, jaar)
        return render.report(report)

#TODO convert to webpage class
class Salaris:
    def get_params(self):

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = config["currentYear"]

        try:
            groep = web.input()['groep']
        except:
            groep = 'TOTAAL'

        return jaar, groep

    def POST(self, userHash):
        return None

    def GET(self, userHash):
        if not webaccess.check_auth(session, userHash, 'salaris'):
            return web.notfound("Sorry the page you were looking for was not found.")
        jaar, groep = self.get_params()
        salaris = websalaris.groep_report(userHash, render, groep, jaar)
        return render.salaris(salaris)


# Checks if IP is allowed
# If not imidialty sends a 404 and stops all processing
def auth_block_by_ip():
    from iptools import IpRangeList
    ip = web.ctx['ip']
    ipRanges = config['IpRanges'].split()
    start = ipRanges[0:][::2]
    stop = ipRanges[1:][::2]

    for start,stop in zip(start,stop):
        ipRange = IpRangeList( (start,stop) )
        if ip in ipRange:
            return

    raise web.notfound()


def auth_login(session, userHash, caller):
    if not session.get('logged_in', False):
        raise web.seeother('/login/%s?caller=%s' %(userHash, caller))


### Url mappings
urls = (
    '/view/(.+)', 'View',
    '/login/(.+)', 'Login',
    '/logout/(.+)', 'Logout',
    '/report/(.+)', 'Report',
    '/salaris/(.+)', 'Salaris',
    '/admin/(.+)', 'Admin',
    '/graph/(.+)/(\d+)/(.*)/(.*).png', 'Graph',
    '/index/(.+)', 'Index',
)

app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session

if __name__ == "__main__":
    app.run()
    print session

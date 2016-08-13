""""
BUGS

    - import multiple files gaat niet goed (stopt na de 1e)

TODO
    - authorisatie in elke class per order/groep/admin. Wellicht via model.isAuthed() doen?
    - user lijst gebruiken om menu te bouwen (ordergroepen voor report!)
    - Show negative bestedingsruimte in red and bold.
    - door pylinter heen halen / pycharm laten controleren ;)
    - report navbar: niet report maar naam van de groep gebruiken, en alle groepen in de dir erin zetten 

# TIPS
    - render.<template>(arg1, arg2, arg3, cache=False) will reload the template file everytime you refresh
"""
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
import webreport
import webview
import websalaris

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


class Report:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'report')
        page = webreport.Report(userHash)
        return page.render()


    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'report')
        page = webreport.Report(userHash)
        return page.render()

class View:
    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'view')
        page = webview.View(userHash)
        return page.render()


    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'view')
        page = webview.View(userHash)
        return page.render()

class Salaris:
    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'salaris')
        page = websalaris.Salaris(userHash)
        return page.render()

    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'salaris')
        page = websalaris.Salaris(userHash)
        return page.render()


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

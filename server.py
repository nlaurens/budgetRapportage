""""
TODO

 - 'AFREKORD' grootboek weer toevoegen alleen als hij ook bestaat voor die orders.

 - kpl support toevoegen

 - WBS support toevoegen (betekend lijst maken met welk wbs bij welke groep hoort..)

- Show negative bestedingsruimte in red and bold.

- Merge overview en view class (lots of double code)

 - ik bedacht me later dat het misschien een goed idee is om boven alle tabbladen de boodschap te zetten in boldface:
Notice that these records show only transactions up to (datum van laatste update)

- Rewrite templates to be more modular with css and header parts:
    http://webpy.org/cookbook/layout_template


"""
import web
import model
import GrootBoek
from config import config
from functions import moneyfmt, IpBlock


class Index:
    def __init__(self):
        pass

    def GET(self):
        return render.index()


class Overview:
    def __init__(self):
        pass

    def GET(self, userHash):
        if userHash == '' or not IpBlock(web.ctx['ip'], config['IpRanges']):
            return web.notfound("Sorry the page you were looking for was not found.")

        if not session.get('logged_in', False):
            raise web.seeother('/login/' + userHash)

        budgets = model.get_budgets(userHash, config["salt"])
        if not budgets:
            return web.notfound("Sorry the page you were looking for was not found.")

        maxdepth = 1

        try:
            KSgroep = int(web.input()['KSgroep'])
        except:
            KSgroep = 0
        KSgroepen = model.loadKSgroepen()
        grootboek = KSgroepen[KSgroep]

        sapdatum = config['lastSAPexport']
        reserves = model.get_reserves()
        begroting = model.get_begroting()

        headers = ['Order', 'Reserve op 1 jan', 'Begroting',  'Bestedingsruimte']

        headersgrootboek = {}
        root = GrootBoek.load(0, grootboek)
        for child in root.children:
            if child.name != 'AFREKORD':
                headersgrootboek[child.name] = child.descr

        orders = []
        for order in budgets:
            line = {}
            root = GrootBoek.load(order, grootboek)

            line['order'] = order

            try:
                line['reserve'] = float(reserves[str(order)])
            except:
                line['reserve'] = 0

            try:
                line['begroting'] = float(begroting[str(order)])
            except:
                line['begroting'] = 0

            if line['reserve'] < 0:
                line['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + line['begroting'] + line['reserve']
            else:
                line['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + line['begroting']

            for child in root.children:
                line[child.name] = moneyfmt((-1*(child.totaalGeboektTree + child.totaalObligosTree)))

            line['reserve'] = moneyfmt(line['reserve'])
            line['ruimte'] = moneyfmt(line['ruimte'])
            line['begroting'] = moneyfmt(line['begroting'])
            orders.append(line)

        return render.overview(headers, headersgrootboek, orders, sapdatum, grootboek, userHash)


class View:
    def __init__(self):
        pass

    def GET(self, userHash, order):

        if userHash == '' or not IpBlock(web.ctx['ip'], config['IpRanges']):
            return web.notfound("Sorry the page you were looking for was not found.")

        if not session.get('logged_in', False):
            raise web.seeother('/login/' + userHash)

        budgets = model.get_budgets(userHash, config["salt"])
        if not budgets:
            return web.notfound("Sorry the page you were looking for was not found.")

        order = int(order)
        try:
            maxdepth = int(web.input()['maxdepth'])
        except:
            maxdepth = 1

        try:
            KSgroep = int(web.input()['KSgroep'])
        except:
            KSgroep = 0
        KSgroepen = model.loadKSgroepen()
        grootboek = KSgroepen[KSgroep]

        sapdatum = config['lastSAPexport']
        root = GrootBoek.load(order, grootboek)
        reserves = model.get_reserves()
        begroting = model.get_begroting()
        totaal = {}
        htmlgrootboek = []

        totaal['order'] = order
        totaal['baten'] = 0
        totaal['lasten'] = 0
        totaal['ruimte'] = 0

        try:
            totaal['reserve'] = float(reserves[str(order)])
        except:
            totaal['reserve'] = 0

        try:
            totaal['begroting'] = float(begroting[str(order)])
        except:
            totaal['begroting'] = 0

        if totaal['reserve'] < 0:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting'] + totaal['reserve']
        else:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting']

        for child in root.children:
            htmlgrootboek.append(child.html_tree(render, maxdepth, 0))
            if child.name == 'BATEN-2900':
                totaal['baten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))
            elif child.name == 'LASTEN2900':
                totaal['lasten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))

        totaal['reserve'] = moneyfmt(totaal['reserve'])
        totaal['ruimte'] = moneyfmt(totaal['ruimte'])
        totaal['baten'] = moneyfmt(totaal['baten'])
        totaal['lasten'] = moneyfmt(totaal['lasten'])
        totaal['begroting'] = moneyfmt(totaal['begroting'])

        if str(order)[4] != '0' and str(order)[4] != '1':
            return render.viewproject(grootboek, sapdatum, htmlgrootboek, totaal)

        return render.vieworder(grootboek, sapdatum, htmlgrootboek, totaal)

class Login:
    login_form = web.form.Form(
        web.form.Password('password', web.form.notnull),
        web.form.Button('Login'),
        )

    def GET(self, userHash):
        form = self.login_form()
        return render.login(form, msg='')

    def POST(self, userHash):
        form = self.login_form()
        if not form.validates():
            return render.login(form)

        if form['password'].value == config["globalPW"]:
            session.logged_in = True
            raise web.seeother('/overview'+userHash)

        return render.login(form, 'Wrong Password')

class Logout:
    def __init__(self):
        pass

    def GET(self):
        session.logged_in = False
        return render.logout()


### Url mappings
urls = (
    '/', 'Index',
    '/overview/(.+)', 'Overview',
    '/view/(.+)/(\d+)', 'View',
    '/login(.+)', 'Login',
    '/logout', 'Logout',
)

### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates/')
app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session

if __name__ == "__main__":
    model.gen_auth_list(config['salt'])
    app.run()

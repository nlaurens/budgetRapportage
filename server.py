""""
BUGS

  - Baten verdwijnen
  - SQL inject in model bekijken

TODO

- 'prognose' posten toevoegen.
- verplaats alle decode/encode naar model (db_2_regel)

- Het kan zijn dat er begroting is op een KS die niet geboekt is. Dan komt hij NIET in het overzicht. FIXEN!

- Importeer functie maken die vraagt om welke kolom wat bevat (namen zijn strings die iedereen apart instelt in SAP....)

 - 'AFREKORD' grootboek weer toevoegen alleen als hij ook bestaat voor die orders.

 - kpl support toevoegen

 - WBS support toevoegen (betekend lijst maken met welk wbs bij welke groep hoort..)

- Show negative bestedingsruimte in red and bold.

- Merge overview en view class (lots of double code)

 - ik bedacht me later dat het misschien een goed idee is om boven alle tabbladen de boodschap te zetten in boldface:
Notice that these records show only transactions up to (datum van laatste update)

- Rewrite templates to be more modular with css and header parts:
    http://webpy.org/cookbook/layout_template

Somday/Maybe:

#cool d3 ding:
- http://bl.ocks.org/NPashaP/96447623ef4d342ee09b
"""
import web
web.config.debug = True #Set to False for no ouput! Must be done before the rest
import model
import GrootBoek
import GrootBoekGroep
import os
from config import config

# web-pages
import webaccess
import webreport
import websalaris
import webadmin
import webview


class Index:
    def __init__(self):
        pass

    def GET(self):
        return render.index()

class View:
    settings_form = web.form.Form(
        #web.form.Checkbox("lovelycheckbox", description="lovelycheckbox", class_="standard", value="something.. Anything!"),
        web.form.Dropdown('jaar', [(2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012')]),
        web.form.Dropdown('maxdepth', [(0,'1. Totals'), (1,'2. Subtotals'), (10, '3. Details')]),
        web.form.Dropdown('ksgroep', []),
        web.form.Checkbox('clean'),
        web.form.Dropdown('periode', [('', 'all')]),
        web.form.Button('Update', 'update'),
    )
    def __init__(self):
        pass

    def fill_dropdowns(self, form, settings, KSgroepen):
        dropdownlist = []
        for i, path in enumerate(KSgroepen):
            dropdownlist.append( (i, os.path.split(path)[-1] ))
        form.ksgroep.args = dropdownlist

        form.ksgroep.value = settings["KSgroep"]
        form.jaar.value = settings["jaar"]
        form.maxdepth.value = settings["maxdepth"]
        form.periode.value = settings["periode"]
        form.clean.checked = settings["clean"]


    def get_post_params(self, form):
        maxdepth = form['maxdepth'].value
        if maxdepth is None:
            try:
                maxdepth = int(web.input()['maxdepth'])
            except:
                maxdepth = 1

        KSgroep = form['ksgroep'].value
        if KSgroep is None:
            try:
                KSgroep = int(web.input()['ksgroep'])
            except:
                KSgroep = 0

        jaar = form['jaar'].value
        if jaar is None:
            try:
                jaar = int(web.input()['jaar'])
            except:
                jaar = 2015

        periode = form['periode'].value
        if periode is None:
            try:
                periode = int(web.input()['periode'])
            except:
                periode = ''

        clean = web.input().has_key('clean')

        return {"maxdepth":maxdepth, "KSgroep":KSgroep, "jaar":jaar, "periode":periode, "clean":clean}

    def POST(self, userHash, order):
        form = self.settings_form
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        KSgroepen = model.loadKSgroepen()
        self.fill_dropdowns(form, settings, KSgroepen)
        return webview.view(render, KSgroepen, form, settings, order)

    def GET(self, userHash, order):
        form = self.settings_form
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        KSgroepen = model.loadKSgroepen()
        settings["clean"] = True
        self.fill_dropdowns(form, settings, KSgroepen)

        return webview.view(render, KSgroepen, form, settings, order)


class Report:
    def get_params(self):

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = 2015

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
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")
        jaar, periode, groep = self.get_params()
        report = webreport.groep_report(userHash, render, groep, jaar)
        return render.report(report)


class Salaris:
    def get_params(self):

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = 2015

        try:
            groep = web.input()['groep']
        except:
            groep = 'TOTAAL'

        return jaar, groep

    def POST(self, userHash):
        return None

    def GET(self, userHash):
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")
        jaar, groep = self.get_params()
        salaris = websalaris.groep_report(userHash, render, groep, jaar)
        return render.salaris(salaris)


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
            raise web.seeother('/report'+userHash)

        return render.login(form, 'Wrong Password')

class Admin:
    upload_form = web.form.Form(
        web.form.File('myfile'),
        web.form.Dropdown('Type', [('', ''),('geboekt','Realisatie'), ('obligo','Obligo'), ('plan', 'Begroting Orders'), ('salaris', 'Salarissen'), ('salaris_begroting', 'Begroting Salarissen')]),
        web.form.Button('Upload data'),
        )

    def GET(self):
        form = self.upload_form()
        msg = webadmin.checkDB()
        return render.webadmin_overview(form, msg)

    def POST(self):
        form = self.upload_form()
        msg = webadmin.parse_form(render, form)
        return render.webadmin_overview(form, msg)


class Logout:
    def __init__(self):
        pass

    def GET(self):
        session.logged_in = False
        return render.logout()


### Url mappings
urls = (
    '/', 'Index',
    '/view/(.+)/(\d+)', 'View',
    '/login(.+)', 'Login',
    '/logout', 'Logout',
    '/report/(.+)', 'Report',
    '/salaris/(.+)', 'Salaris',
    '/admin', 'Admin',
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

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
import OrderGroep
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
            groepen = model.loadKSgroepen()
            match =  [s for s in groepen if "WNMODEL4" in s][0]
            KSgroep = groepen.index(match)

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = 2016

        try:
            periode = int(web.input()['periode'])
        except:
            periode = 0

        clean = web.input().has_key('clean')

        return {"maxdepth":maxdepth, "KSgroep":KSgroep, "jaar":jaar, "periode":periode, "clean":clean}

    def POST(self, userHash, order):
        form = self.settings_simple_form
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        return webview.view(settings, render, form, order)

    def GET(self, userHash, order):
        form = self.settings_simple_form
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")

        settings = self.get_post_params(form)
        settings["clean"] = True
        return webview.view(settings, render, form, order)


class Report:
    def get_params(self):

        try:
            jaar = int(web.input()['jaar'])
        except:
            jaar = 2016

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
            jaar = 2016

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
    sapdate_form = web.form.Form(
        web.form.Textbox('Sapdate'),
        web.form.Button('Update'),
        )
    graphsUpdate_form = web.form.Form(
        web.form.Textbox('Ordergroep'),
        web.form.Button('Refresh Graphs'),
        )

    def GET(self):
        msg = webadmin.checkDB()
        msg.append('')
        msg.append('latest sap date: ' + model.last_update())

        return render.webadmin_overview(self.upload_form, self.sapdate_form, self.graphsUpdate_form, msg)

    def POST(self):
        if 'Update' in web.input():
            msg = ['Updating last sap update date']
            model.last_update(web.input()['Sapdate'])
            msg.append('DONE')
        if 'Upload data' in web.input():
            msg = webadmin.parse_upload_form(render, self.upload_form)
        if 'Refresh Graphs' in web.input():
            msg = webadmin.updateGraphs(web.input()['Ordergroep'])
        return render.webadmin_overview(self.upload_form, self.sapdate_form, self.graphsUpdate_form, msg)


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

""""
BUGS

  - Baten verdwijnen

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
web.config.debug = True #must be done before the rest.
import model
import GrootBoek
import GrootBoekGroep
import os
from config import config
from functions import moneyfmt, IpBlock

# web-pages
import webaccess
import webreport
import websalaris
import webadmin


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

    def view(self, userHash, order, parent):
        if not webaccess.check_auth(session, userHash):
            return web.notfound("Sorry the page you were looking for was not found.")

        form = self.settings_form()
        KSgroepen = model.loadKSgroepen()
        settings = self.get_post_params(form)
        if parent == 'GET':
            settings["clean"] = True
        self.fill_dropdowns(form, settings, KSgroepen)

        order = int(order)
        grootboek = KSgroepen[settings["KSgroep"]]
        sapdatum = config['lastSAPexport']

        root = GrootBoek.load(order, grootboek, settings["jaar"], settings["periode"])
        if settings["clean"]:
            root.clean_empty_nodes()

#TODO Begroting uit sap 'plan' halen!
        #begroting = model.get_begroting() # dit is de oude functie van VU
        totaal = {}
        htmlgrootboek = []

        totaal['order'] = order
        totaal['baten'] = 0
        totaal['lasten'] = 0
        totaal['ruimte'] = 0

        reserves = model.get_reserves()
        try:
            totaal['reserve'] = reserves[str(order)]
        except:
            totaal['reserve'] = 0


        totaal['begroting'] = 0#float(begroting[str(order)])

        if totaal['reserve'] < 0:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting'] + totaal['reserve']
        else:
            totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting']

        for child in root.children:
            htmlgrootboek.append(child.html_tree(render, settings["maxdepth"], 0))
# TODO: DIT IS SPECIFIEK VOOR 29FALW2
            if child.name == 'BATEN-2900':
                totaal['baten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))
            elif child.name == 'LASTEN2900':
                totaal['lasten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))

        totaal['reserve'] = moneyfmt(totaal['reserve'])
        totaal['ruimte'] = moneyfmt(totaal['ruimte'])
        totaal['baten'] = moneyfmt(totaal['baten'])
        totaal['lasten'] = moneyfmt(totaal['lasten'])
        totaal['begroting'] = moneyfmt(totaal['begroting'])

# TODO: INFO ERGENS ANDERS VANDAAN HALEN VOOR UL
        #if str(order)[4] != '0' and str(order)[4] != '1':
            #return render.viewproject(grootboek, sapdatum, htmlgrootboek, totaal)

        #print '----------------'
        #root.walk_tree(9999)
        return render.vieworder(form, grootboek, sapdatum, htmlgrootboek, totaal)

    def POST(self, userHash, order):
        return self.view(userHash, order, 'POST')

    def GET(self, userHash, order):
        return self.view(userHash, order, 'GET')

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
        x = web.input(myfile={})
        filedir = './data' # change this to the directory you want to store the file in.
        allowed = ['.txt', '.xlsx', '.xls', '.cvs']
        
        msg = ['Uploading file.']
        succes_upload = False
        if 'myfile' in x: 
            pwd, filenamefull = os.path.split(x.myfile.filename)
            filename, extension = os.path.splitext(filenamefull)
            if extension in allowed:
                fout = open(filedir +'/'+ filenamefull,'wb')
                fout.write(x.myfile.file.read()) 
                fout.close() 
                succes_upload = True

        if not succes_upload:
            msg.append('upload failed!')
            return render.webadmin_overview(form, msg)

        msg.append('upload succes')
        table = web.input()['Type']
        table_allowed = False
        if table in ['geboekt', 'obligo', 'plan', 'salaris', 'salaris_begroting']:
            table_allowed = True

        if not table_allowed:
            msg.append('Type not selected!')
            return render.webadmin_overview(form, msg)

        msg.append('Preparing to process data for table: ' + table)

        # excel -> csv
        # extract headers csv
        # Move old table -> backup
        # Create new table (use csv headers!)
        # Fill table from CSV
        # clean up

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

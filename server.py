""""
#BUGS


#TODO

General
  * Remove hardcoded 'geboekt', 'obligo', etc. from all model/controller - grep
  * Alle templates doorlopen op $:xxx als dat niet nodig is.
  * Navbar is build on 2 recursive functions. Replace by ordergroup.list_groups(Inverted=True)
    That function should give you the exact list that you need.

Auth-module
  * add settings for table names (user, permission, user_permission as standard)

Graph-module
  * graph groups should be named: <ordergroup_file_name><ordergroup_name>

Model-modules
  -.regels
    * merge .last_update and .last_period to general mysql.config read/writer
    * add reserve to db

  -.budget.kostensoortgruop
    * remove regels from class. Should all be done in the controller.

Controller-modules
  - Controller-superclass
    * user lijst gebruiken om menu te bouwen (ordergroepen voor report!)
    * build list of allowed orders/ordergroups based on models.user.permissions

  - view
      * move periode check, All, Q, etc code from __init__ to controller master class 
      * add config params/forms
      * Address color_mapping in __init__ 
        code copied from graph.py. Perhaps do the mapping in model.ksgroups, and load the color scheme from config?
        It really feels like we made the model.budget.ksgroup object redundant with the regellist and ksgroup hashmap
      * Set title of view

  - admin
      * Option to delete SAP table
      * create test that looks if there are orders in db not in any ordergroup
        (and perhaps also look at the GS)
      * add 'year' field in table for salaris geboekt based on the boekingsdate.
      * add simple create/modify user tools. Now done from the config file.
      * Update graphs:
          . Re-enable building graphs from admin menu.
          . replace order/group with dropdown box and force only inputs from that box
          . Add polling option for status rebuilding graphs process.

  - salaris
      * Refactor the data-dict in create_data_structure. Currently it has a lot of double
        code ('salarisplan:0, ..), could be replaced with a deepcopy of a empty 'total' dictionary
      * settings maken
      * Plaatjes maken/koppelen
      * Add mouse-over information for payrollnummers that shows all personeelsnummers that are linked to payrollnummer

  - report
      * Split into 4 tabs:
        * Remove details if there are no subgroups
        * Add divs to the graph page

  - orderlist
      * add option to sort by budgetholder
      * add javascript for collapse +/- buttons in process_sub
"""
import sys,os
import web
web.config.debug = True  # Set to False for no ouput! Must be done before the rest

# Apache WSGI requires path and working dir to be changed for importing own modules
app_path= os.path.dirname(__file__)
sys.path.append(app_path)
if app_path:
    os.chdir(app_path)

# By using strings for the controller classes insteaf of from controller import 
# X,Y,Z the modules are reloaded when running the web.py built in server
urls = (
    '/', 'controller.index.Index',
    '/index', 'controller.index.Index',
    '/orderlist', 'controller.orderlist.Orderlist',
    '/salaris', 'controller.salaris.Salaris', 
    '/report(.*)', 'controller.report.Report', 
    '/view(.*)', 'controller.view.View', 
    '/admin', 'controller.admin.Admin', 

    '/graph/(.+)/(.+)/(.+).png', 'controller.graph.Graph', 

    '/login', 'auth.handlers.Login',  
    '/logout', 'auth.handlers.Logout', 
)

# with WSGI:
app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session

from auth import auth 
from model.functions import db
from config import config
auth.init_app(app, db, session, **config["auth"]["settings"])

application = app.wsgifunc()

if __name__ == "__main__":
    if sys.argv[-1] == '--init':
        from config import init_auth_db      
        print 'Setting up auth db'
        init_auth_db(db)
        print 'You can now login with your admin user from the config.'
        exit()
    else:
        app.run()

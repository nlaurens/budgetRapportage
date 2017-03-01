""""
BUGS



TODO

Remove hardcoded 'geboekt', 'obligo', etc. from all model/controller - grep
    - model.orders maken die dict retourned met order name from mysql and excel import

Auth
    - add settings for table names (user, permission, user_permission as standard)

Graph
    - graph groups should be named: <ordergroup_file_name><ordergroup_name>

Model
    - model.users
        * ouser lijst gebruiken om menu te bouwen (ordergroepen voor report!)

    - regels
        * write validator for input that can be re-used (tablename in config[''] etc.)
        * add reserve to db

    - orderlist
        * add (merge it with regels)
        * make model.budget.orderlist class that behavious similar to other budget classes
        * sort orderlist on act. code and show them in different collapsoable tables.

Config
    - config module maken waar ook alle data in zit en users
    - alle config params naar db verplaatsen -> model

Controller & Webpages
    - Alle templates doorlopen op $:xxx als dat niet nodig is.
    - Navbar is build on 2 recursive functions. Replace by ordergroup.list_groups(Inverted=True)
      That function should give you the exact list that you need.

    - view
        * html_tree has double code, lot of it is done by budget.kostensoortgroup

    - admin
        * forms layout doen (attributen van webpy forms setten)
        * create test that looks if there are orders in db not in any ordergroup
          (and perhaps also look at the GS)
        * add 'year' field in table for salaris geboekt based on the boekingsdate.
        * add simple create/modify user pages

    - login
        * bij password verkeerd invullen post form leegmaken.

    - salaris
        * settings maken
        * Plaatjes maken/koppelen

    - report
        * aantal voorgaande jaren in settings

    -graph

# TIPS
    - render.<template>(arg1, arg2, arg3, cache=False) will reload the template file everytime you refresh

"""
import sys,os
import web
web.config.debug = True  # Set to False for no ouput! Must be done before the rest

# Apache WSGI requires path and working dir to be changed for importing own modules
app_path= os.path.dirname(__file__)
sys.path.append(app_path)
if app_path:
    os.chdir(app_path)

from controller import Index, Report, Admin, Graph, View, Salaris, Orderlist
from auth.handlers import Login, Logout

urls = (
    '/', 'Index',
    '/index', 'Index',
    '/orderlist', 'Orderlist', 
    '/salaris', 'Salaris', 
    '/report(.*)', 'Report', 
    '/view(.*)', 'View', 
    '/admin', 'Admin', 

    '/graph/(.+)/(.+)/(.+).png', 'Graph', 

    '/login', 'Login',  #uses auth.handlers.Login
    '/logout', 'Logout', # auth.handlers.Logout
)

app = web.application(urls, globals())

from auth import auth 
from model.functions import db
from config import config
auth.init_app(app, db, **config["auth"]["settings"])

application = app.wsgifunc()

if __name__ == "__main__":
    if sys.argv[-1] == '--init':
        print 'creating tables'
        for table in config['auth']['tables']:
            db.query(table)
        print 'creating permissions and users'
        auth.create_permission('admin', 'Has access to admin panel')
        auth.create_user('admin', password='123admin', perms=['admin'])
        print 'done.'
        exit()
    else:
        app.run()

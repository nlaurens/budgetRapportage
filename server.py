""""
BUGS



TODO

Remove hardcoded 'geboekt', 'obligo', etc. from all model/controller - grep
    - model.orders maken die dict retourned met order name from mysql and excel import

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

    - login
        * bij password verkeerd invullen post form leegmaken.

    - salaris
        * settings maken
        * Plaatjes maken/koppelen

    - report
        * aantal voorgaande jaren in settings

    -graph
        * userHash checken - alles staat nu op

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

from controller import Index, Report, Admin, Login, Logout, Graph, View, Salaris, Orderlist

urls = (
    '/view/(.+)', 'View',
    '/login/(.+)', 'Login',
    '/logout/(.+)', 'Logout',
    '/report/(.+)', 'Report',
    '/salaris/(.+)', 'Salaris',
    '/orderlist/(.+)', 'Orderlist',
    '/admin/(.+)', 'Admin',
    '/graph/(.+)/(.+)/(.+)/(.+).png', 'Graph',
    '/index/(.+)', 'Index',
)

# with WSGI:
app = web.application(urls, globals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
    web.config._session = session
else:
    session = web.config._session
application = app.wsgifunc()

# withouth WSGI
if __name__ == "__main__":
    app.run()

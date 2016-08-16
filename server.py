""""

BUGS


TODO

Remove hardcoded 'geboekt', 'obligo', etc. from all model/controller - grep

Model
    - model.users
        * ouser lijst gebruiken om menu te bouwen (ordergroepen voor report!)

    - regels
        * write validator for input that can be re-used (tablename in config[''] etc.)
        * add reserve to db

Config
    - config module maken waar ook alle data in zit en users
    - alle config params naar db verplaatsen -> model

Controller & Webpages
    - Alle templates doorlopen op $:xxx als dat niet nodig is.

    - view
        * html_tree has double code, lot of it is done by budget.kostensoortgroup

    - admin
        * forms layout doen (attributen van webpy forms setten)
        * create test that looks if there are orders in db not in any ordergroup
          (and perhaps also look at the GS)

    - login
        * bij password verkeerd invullen post form leegmaken.

    - salaris
        * Naam order uit andere db halen, salaris geeft korte namen.. (kostensoort groep?)
        * Plaatjes maken/koppelen
        * Summary van alle totalen maken (totalOrderGeboekt, etc opvangen uit html_table)
        * Obligos salarissen ECHT uit systeem halen (kan! ipv de HR-obligos per order!)

    - report
        * try to make .css to adjust colors for each div/table so its easier to see
        * settings: &flat={1,0}
        * Show negative bestedingsruimte in red and bold.

    -graph
        * userHash checken - alles staat nu op

# TIPS
    - render.<template>(arg1, arg2, arg3, cache=False) will reload the template file everytime you refresh
"""
import web
web.config.debug = True #Set to False for no ouput! Must be done before the rest
from controller import Index, Report, Admin, Login, Logout, Graph, View, Salaris

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

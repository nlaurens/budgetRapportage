""""
BUGS

    - import multiple files gaat niet goed (stopt na de 1e)

TODO
    - Model, View, Controller .. Heb nu View en Controller in 1 gemaakt.. Splitsen dus!
    - authorisatie in elke class per order/groep/admin. Wellicht via model.isAuthed() doen?
    - user lijst gebruiken om menu te bouwen (ordergroepen voor report!)
    - Show negative bestedingsruimte in red and bold.
    - door pylinter heen halen / pycharm laten controleren ;)
    - report navbar: niet report maar naam van de groep gebruiken, en alle groepen in de dir erin zetten
    - config module maken waar ook alle data in zit en users
        - users in mysql maken
        - alle config params naar db verplaatsen

# TIPS
    - render.<template>(arg1, arg2, arg3, cache=False) will reload the template file everytime you refresh
"""
import web
web.config.debug = True #Set to False for no ouput! Must be done before the rest
import os
from config import config

import webpage
import budget

from controller import Index, Report, Admin, Login, Logout, Graph, View, Salaris

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
#TODO remove debug line
    return
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

import web
from config import config
from functions import IpBlock

#AUTH
def check_auth(session, userHash):
    if not session.get('logged_in', False):
        raise web.seeother('/login/' + userHash)

    IPAllowed= IpBlock(web.ctx['ip'], config['IpRanges'])
    if userHash == '' or not IPAllowed:
        return False
    return True

#LOGIN form
def loginform(url):
    login_form = web.form.Form(
        web.form.Password('password', web.form.notnull),
        web.form.Hidden('redirect', value=url),
        web.form.Button('Login'),
    )
    return login_form

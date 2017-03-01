from auth import auth

"""
.protected()
Decorator to protect functions. We use the auth.protect method:
    @protected([perm][, captcha_on][, test])

    Decorator for limiting the access to pages.

    'perm' can be either a single permission (string) or a sequence of them.

    'captcha_on' is a Boole value('True' or 'False') to turn on or off the
    captcha validation.

    'test' must be a function that takes a user object and returns
    True or False.
"""
def protected(**pars):
    return auth.protected(**pars)

"""
.get_users()
    Returns a list of all users and their permissions/info
"""
def get_users():
    users = []
    users.append({'username':'Niels', 'permissions':'admin, bfr', 'last_login':'yesterday', 'status':'Active'})
    users.append({'username':'henk', 'permissions':'admin, bfr', 'last_login':'yesterday', 'status':'Active'})
    users.append({'username':'piet', 'permissions':'admin, bfr', 'last_login':'yesterday', 'status':'Active'})
    return users 

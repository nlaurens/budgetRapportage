from auth import auth

"""
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

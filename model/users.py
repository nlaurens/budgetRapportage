from auth import auth

def protected(**pars):
    """
    .protected()
    Decorator to only allowed login users. We use the auth.protect method. Note 
    that this method can only be used on the 'top' level function (GET) as it re-
    directs directly and thus fails on nested functions.

        @protected([perm][, captcha_on][, test])

        Decorator for limiting the access to pages.

        'perm' can be either a single permission (string) or a sequence of them.

        'captcha_on' is a Boole value('True' or 'False') to turn on or off the
        captcha validation.

        'test' must be a function that takes a user object and returns
        True or False.
    """
    return auth.protected(**pars)


def get_users():
    """
    .get_users()
        Returns a list of all users and their permissions/info
    """
    return auth.get_all_users()


def get_permissions():
    """
    .get_users()
        Returns a list of all permissions and their description
    """
    return auth.get_all_permissions()


def check_permission(perm):
    """
    .check_permissions(perm)
        input: perm as string or list of strings
        output: True/False
        Checks if current user has (all) permissions: True, otherwise
        returns False
    """
    return auth.has_perm(perm)


def orders_allowed():
    """
    .orders_allowed()
        input: none
        output: List of orders (int) that user has access too based
        on the ordergroups he has permission for.
    """
    perimssions = ['ordergroup-LION-OL-FMD', 'ordergroup-LION-PL-TP']  #replace by auth.xxx
    for permission in permissions:
        ordergroup, group = __parse_ordergroup_permission(permission)

    orders = [2008501040, 20081204110] #ordergroup.get_orders_recursive(groups) 

    return orders

def __parse_ordergroup_permission(permission):
    """
    .__parse_ordergroup_permission(permission)
        input: permission as str
        output: ordgergroup as str, group in ordergroup as str
    """
    permission_as_list = permission.split('-')
    ordergroup = permission_as_list[1]
    group = '-'.join(permission_as_list[1:])

    return ordergroup, group

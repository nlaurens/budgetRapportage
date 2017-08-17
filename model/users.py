from auth import auth
import model.ordergroup

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
    .get_permissions()
        Returns a list of all permissions and their description
    """
    return auth.get_all_permissions()

def get_username():
    """
    .get_username()
        Returns a the name (str) of the logged in user
    """
    return auth.get_user().user_login


def get_permission():
    """
    .get_permission()
        Returns a list of all permissions of the logged in user
    """
    permissions = auth.get_permissions()
    if isinstance(permissions, str):
        return [permissions]
    return permissions


def check_permission(perm):
    """
    .check_permissions(perm)
        input: perm as string or list of strings
        output: True/False
        Checks if current user has (all) permissions: True, otherwise
        returns False
    """
    return auth.has_perm(perm)


def check_ordergroup(og_file, og_name):
    """
    .check_ordegroup(og_file, og_name)
        input: og_file as string, og_name as string
        output: True/False
        Checks if user has access to ordegroup 'og_name' in ordegroupfile 'og_file'
        returns True if both match, otherwise False
    """
    ordergroups_allowed = model.users.ordergroups_allowed()
    for ordergroup_file_allowed, ordergroup_allowed in ordergroups_allowed:
        ordergroup = model.ordergroup.load(ordergroup_file_allowed).find(ordergroup_allowed)
        for subordergroup in ordergroup.list_groups():
            if subordergroup.name == og_name and ordergroup_file_allowed == og_file:
                return True

    return False


def ordergroups_allowed():
    """
    .orders_allowed()
        input: none
        output: List of ordersgroups and the file that user has permission for:
                [ (ordergroup-file, ordergroup), (.. , ..)]
    """
    ordergroups_allowed = []
    permissions = get_permission()
    for permission in permissions:
        if permission[:10] == 'ordergroup':
            ordergroup, group = __parse_ordergroup_permission(permission)
            ordergroups_allowed.append((ordergroup, group))

    return ordergroups_allowed


def orders_allowed():
    """
    .orders_allowed()
        input: none
        output: List of orders (int) that user has access too based
        on the ordergroups he has permission for.
    """
    orders = []
    for ordergroup, group in ordergroups_allowed():
        ordergroup = model.ordergroup.load(ordergroup).find(group)
        orders.extend(ordergroup.list_orders_recursive().keys())

    return orders

def __parse_ordergroup_permission(permission):
    """
    .__parse_ordergroup_permission(permission)
        input: permission as str
        output: ordgergroup as str, group in ordergroup as str
    """
    permission_as_list = permission.split('-')
    ordergroup = permission_as_list[1]
    group = '-'.join(permission_as_list[2:])

    return ordergroup, group

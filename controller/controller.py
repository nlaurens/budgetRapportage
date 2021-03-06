import web
import urllib
from web import form

from config import config

import model.regels
import model.ordergroup
from model.functions import check_connection
from model.users import protected


class Controller(object):
    def __init__(self):
        self.mainRender = web.template.render('webpages/')
        self.config = config
        connected, error = check_connection()
        if not connected:
            raise web.notfound(error[1])
        self.SAPupdate = model.regels.last_update()  # gives subclass__init__ access

        # should be set in the subclass
        self.body = None
        self.title = None
        self.module = None
        self.webrender = None
        self.breadCrum = None  # list of dict items (keys: title, ulr, class:active)
        self.static = False

        # forms
        self.form_redirect = form.Form(
            form.Button('ok', value='redirect')
        )

    # arg: 0 superclass inst., 1 subclass inst. 2. vars from url_map in a tupple
    def GET(*arg):
        self = arg[0]
        self.callType = 'GET'
        return self.process_main(*arg[2:])  # remaining params

    def POST(*arg):
        self = arg[0]
        self.callType = 'POST'
        return self.process_main(*arg[2:])

    @protected()
    def process_main(self, *arg):
        if not self.authorized():
            msg = ['Not authorized.']
            redirect = 'index'
            self.body = self.render_simple(msg, redirect=redirect)
        else:
            self.process_sub(*arg)  # arg = remaining params

        return self.render_page()

    # Should be implemented by subclass
    def authorized(self):
        raise NotImplementedError

    # Should be implemented by subclass
    def process_sub(self):
        raise NotImplementedError

    def render_page(self):
        navgroups = []
        if model.users.check_permission(['report']):
            for ordergroup in model.ordergroup.available():
                navitem = self.navbar_group(ordergroup)
                if navitem:
                    navgroups.append(self.navbar_group(ordergroup))

        show_links = {}
        for module in ['admin', 'orderlist', 'salaris']:
            show_links[module] = model.users.check_permission([module])

        navbar = self.mainRender.navbar(self.breadCrum, navgroups, show_links)
        version = self.config['version']

        return self.mainRender.page(self.title, self.body, self.SAPupdate, version, navbar)

    def navbar_group(self, og):
        # create list of all subgroups that we have access too.
        ordergroups_allowed = model.users.ordergroups_allowed()
        subgroups_allowed = []
        for ordergroup_file_allowed, ordergroup_allowed in ordergroups_allowed:
            if ordergroup_file_allowed == og:
                subgroups_allowed.append(ordergroup_allowed)
        
        navgroups = []
        i = 0
        for subgroup in subgroups_allowed:
            i += 1
            child = model.ordergroup.load(og).find(subgroup)
            navgroups.extend(self.list_nav_groups(og, child, str(i), 1))

        if subgroups_allowed:
            return {'title': og, 'items': navgroups}
        else:
            return {}

    def list_nav_groups(self, og, root, label, depth):
        groups = []
        i = 0
        for child in root.children:
            i += 1
            label_child = '%s.%s' % (label, i)
            groups.extend(self.list_nav_groups(og, child, label_child, depth + 1))

        name = '%s' % root.descr  # you can use: '%s. %s' % (label, root.descr) as numbered list
        link = '/report?ordergroep=%s&subgroep=%s' % (og, root.name)
        padding = str(depth * 15)
        groups.insert(0, {'link': link, 'name': name, 'padding': padding})
        return groups

    # used for creating links in the submodule
    def url(self, module=None, params=None):
        if module is None:
            module = self.module
        if params:
            param_str = urllib.urlencode(params)
            return '/%s?%s' % (module, param_str)
        else:
            return '/%s' % module

    # Returns possible dropdown fills for web.py forms.
    def dropdown_options(self):
        jaren_db = model.regels.years()

        options = {}
        options['empty'] = [('', '')]
        options['all'] = [('*', '! ALL !')]
        options['years'] = zip(jaren_db, jaren_db)
        options['tables'] = self.config['mysql']['tables_regels'].keys()
        options['tables'].append('orderlijst')

        options['months'] = [(1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'),
                             (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')]
        options['Qs'] = [('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')]

        options['periode_all'] = [('ALL', 'all')] + options['Qs'] + options['months']

        options['empty_years_all'] = options['empty'] + options['years'] + options['all']

        options['empty_tables'] = options['empty'] + options['tables']
        options['empty_tables_all'] = options['empty'] + options['tables'] + options['all']

        ordergroups = model.ordergroup.available()
        options['ordergroups'] = zip(ordergroups, ordergroups)
        ordergroups_all = model.ordergroup.available(actcode_groups=True)
        options['ordergroups_all'] = zip(ordergroups_all, ordergroups_all)

        return options

    # display simple message and 'ok' button for redirecting after message
    def render_simple(self, msg, redirect=None):
        if redirect:
            form_redirect = self.form_redirect
            redirect = '/%s' % redirect
        else:
            form_redirect = ''
            redirect = ''

        return self.mainRender.simple(self.title, msg, form_redirect, redirect)

    # Creates url to graph
    # graph_type: realisatie, bars, pie, etc.
    # graph_name: anything from group orders to order numbers.
    # params_list:   {param: value, ..} 
    # returns: /graph/<graph_type>/<ksgroup>/<graph_name>.png?[params]
    def url_graph(self, year, ksgroup, graph_type, name, params=None):

        if params:
            param_str = urllib.ulrencode(params)
            return '/graph/%s/%s/%s/%s.png?%s' % (year, ksgroup, graph_type, name, param_str)
        else:
            return '/graph/%s/%s/%s/%s.png' % (year, ksgroup, graph_type, name)

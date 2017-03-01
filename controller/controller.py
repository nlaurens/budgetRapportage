import web
import urllib
from web import form
from auth import auth

from config import config

import model.regels
import model.ordergroup
from model.functions import check_connection

class Controller(object):
    def __init__(self):
        self.mainRender = web.template.render('webpages/') 
        self.config = config
        connected, error = check_connection()
        if not connected:
            raise web.notfound(error[1])
        self.SAPupdate = model.regels.last_update()  # gives subclass__init__ access

        # should be set in the subclass
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

    # TODO ENABLE THIS
    #@auth.protected()
    def process_main(self, *arg): 
        self.process_sub(*arg)  # arg = remaining params
        
        return self.render_page()

    # Should be implemented by subclass and set self.body
    def process_sub(self):
        raise NotImplementedError
    
    def render_page(self):
# TODO uit usergroup halen - daar zou de ordergroep al in geload moeten zijn!
        navgroups = []
        
        for ordergroup in model.ordergroup.available():
            navgroups.append(self.navbar_group(ordergroup))

        navbar = self.mainRender.navbar(self.breadCrum, navgroups)

        return self.mainRender.page(self.title, self.body, self.SAPupdate, navbar)

    def navbar_group(self, og):
        ordergroup = model.ordergroup.load(og)
        navgroups = []
        i = 0
        for child in ordergroup.children:
            i += 1
            navgroups.extend(self.list_nav_groups(og, child, str(i), 1))

        name = ordergroup.descr
        link = '/report?ordergroep=%s&subgroep=%s' % (og, ordergroup.name)
        padding = str(0)
        navgroups.insert(0, {'link': link, 'name': name, 'padding': padding})

        return {'title': og, 'items': navgroups}

    def list_nav_groups(self, og, root, label, depth):
        groups = []
        i = 0
        for child in root.children:
            i += 1
            label_child = '%s.%s' % (label, i)
            groups.extend(self.list_nav_groups(og, child, label_child, depth+1))

        name = '%s' % root.descr  # you can use: '%s. %s' % (label, root.descr) as numbered list
        link = '/report?ordergroep=%s&subgroep=%s' % (og, root.name)
        padding = str(depth*15)
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
            return '/%s' % (module)


    # Returns possible dropdown fills for web.py forms.
    def dropdown_options(self):
        jaren_db = model.regels.years()

        options = {}
        options['empty'] = [('', '')]
        options['all'] = [('*','! ALL !')]
        options['years'] = zip(jaren_db, jaren_db)
        options['tables'] = self.config['mysql']['tables']['regels'].keys()
        options['tables'].append('orderlijst') 

        options['months'] = [(1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Okt'), (11, 'Nov'), (12, 'Dec')]
        options['Qs'] = [('Q1','Q1'), ('Q2','Q2'),('Q3','Q3'),('Q4','Q4')]

        options['periode_all'] = [('ALL', 'all')] + options['Qs'] + options['months']

        options['empty_years_all'] = options['empty'] + options['years'] + options['all']

        options['empty_tables'] = options['empty'] + options['tables']
        options['empty_tables_all'] = options['empty'] + options['tables'] + options['all']

        ordergroups = model.ordergroup.available()
        options['ordergroups'] = zip(ordergroups, ordergroups)
        ordergroups_all = model.ordergroup.available(actcode_groups=True)
        options['ordergroups_all'] = zip(ordergroups_all, ordergroups_all)

        return options

    # can be used in any class to display a msg or a form
    def render_simple(self):
        if hasattr(self, 'redirect'):
            form_redirect = self.form_redirect
            redirect = '/%s' % (self.redirect)
        else:
            form_redirect = ''
            redirect = ''

        return self.mainRender.simple(self.title, self.msg, form_redirect, redirect)

    # Creates url to graph
    # graph_type: realisatie, bars, pie, etc.
    # graph_name: anything from group orders to order numbers.
    # params_list:   {param: value, ..} 
    # returns: /graph/<user_hash>/<graph_type>/<graph_name>.png?[params]
    def url_graph(self, year, graph_type, name, params=None):

        if params:
            param_str = urllib.ulrencode(params)
            return '/graph/%s/%s/%s.png?%s' % (year, graph_type, name, param_strs)
        else:
            return '/graph/%s/%s/%s.png' % (year, graph_type, name)


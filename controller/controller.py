import web
import model.db

class Controller(object):
    def __init__(self):
#TODO remove cache=False
        self.mainRender = web.template.render('webpages/', cache=False) 

        # should be set in the subclass
        self.title = None
        self.module = None
        self.webrender = None
        self.breadCrum = None #list of dict items (keys: title, ulr, class:active)
        self.static = False

        pass

    def GET(*arg):
        self = arg[0]
        self.callType = 'GET'
        return self.process_main(self, arg[1:])

    def POST(*arg):
        self = arg[0]
        self.callType = 'POST'
        return self.process_main(arg)

    def process_main(*arg):
        self = arg[0]
        self.check_IP_allowed() # Will terminate all non-auth. connections 

        self.userHash = arg[1]
        self.SAPupdate = model.db.last_update()
#TODO re-implement this
        #if not session.get('logged_in', False):
            #TODO: determine the caller'
            #raise web.seeother('/login/%s?caller=%s' %(userHash, caller))
        
        self.process_sub(arg) #sets the self.body, title
        return self.render_page()

    # Should be implemented by subclass and set self.body
    def process_sub(self):
        raise NotImplementedError
    
    # self.body should have been rendered by subproc
    def render_page(self):
        navgroups = self.navbar_groups()
        navbar = self.mainRender.navbar(self.userHash, self.breadCrum, navgroups)
        return self.mainRender.page(self.title, self.body, self.SAPupdate, navbar)

    #def set_page_attr(self, page):
    #    for attr, value in self.pageAttr.iteritems():
    #        setattr(page, attr, value)

    def navbar_groups(self):
        #Navigation bar including a dropdown of the report layout
#TODO uit usergroup halen - daar zou de ordergroep al in geload moeten zijn!
        #orderGroep = OrderGroep.load('LION')
        #groups = []
        #i = 0
        #for child in orderGroep.children:
        #    i += 1
        #    groups.extend( self.render_navigation(child, str(i), 1))

        #name = orderGroep.descr
        #link = '/report/%s?groep=%s' % (self.userHash, orderGroep.name)
        #padding = str(0)
        #groups.insert(0,{'link': link, 'name':name, 'padding':padding})
        return ''

    #used for creating links in the submodule
    def url(self):
        return ('/%s/%s' % (self.module, self.userHash))

    # Checks if IP is allowed
    # If not imidialty sends a 404 and stops all processing
    def check_IP_allowed(self):
        from config import config
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

    # Returns possible dropdown fills for web.py forms.
    def dropdown_options(self):
        jarenDB = model.db.get_years_available()

        options = {}
        options['empty'] = [ ('', '')]
        options['all'] = [ ('*','! ALL !') ]
        options['years'] = zip(jarenDB, jarenDB)
        options['tables'] = config['mysql']['tables']['regels'].items()

        options['empty_years_all'] = options['empty'] + options['years'] + options['all']

        options['empty_tables'] = options['empty'] + options['tables']
        options['empty_tables_all'] = options['empty'] + options['tables'] + options['all']

        return options

    # can be used in any class to display a msg or a form
    def render_simple(self):
        if hasattr(self, 'redirect'):
            form = self.form_redirect
            redirect = '/%s/%s' % (self.redirect, self.userHash)
        else:
            form = ''
            redirect = ''

        return self.mainRender.simple(self.title, self.msg, form, redirect)


import web
from web import form
import model
from config import config
import OrderGroep

# Mother class for all webpages
class Webpage(object):
    def __init__(self, userHash, static=False):
        self.userHash = userHash
        self.static = static
        self.mainRender = web.template.render('templates/', cache=False) #in init cause subclasses might also access it
        print 'WARNING DEBUG CODE STILL ON '
        print 'WARNING DEBUG CODE STILL ON '
        print 'WARNING DEBUG CODE STILL ON '
        self.dropDownOptions = self.dropdown_options()

        # should be set in the subclass
        self.title = None
        self.module = None
        self.webrender = None
        self.breadCrum = None #list of dict items (keys: title, ulr, class:active)
        self.SAPupdate = model.last_update()


    def render(self):
        self.render_body() #Start with rendering subclass in case it sets breadcrums etc.
#TODO cache renderd page and check if we can serve that

        #Navigation bar including a dropdown of the report layout
#TODO to config
        orderGroep = OrderGroep.load('LION')
        groups = []
        i = 0
        for child in orderGroep.children:
            i += 1
            groups.extend( self.render_navigation(child, str(i), 1))

        name = orderGroep.descr
        link = '/report/%s?groep=%s' % (self.userHash, orderGroep.name)
        padding = str(0)
        groups.insert(0,{'link': link, 'name':name, 'padding':padding})
        navbar = self.mainRender.navbar(self.userHash, self.breadCrum, groups)

        return self.mainRender.page(self.title, self.body, self.SAPupdate, navbar)

    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError

#Niet extended maar inserten!
    def render_navigation(self, root, label, depth):
        groups = []
        i = 0
        for child in root.children:
            i += 1
            labelChild = '%s.%s' % (label, i)
            groups.extend(self.render_navigation(child, labelChild, depth+1))

        name = '%s' % (root.descr) #you can use: '%s. %s' % (label, root.descr) as numbered list
        link = '/report/%s?groep=%s' % (self.userHash, root.name)
        padding = str(depth*15)
        groups.insert(0,{'link': link, 'name':name, 'padding':padding})
        return groups



    #used for creating links in the submodule
    def url(self):
        return ('/%s/%s' % (self.module, self.userHash))


    # Returns possible dropdown fills for web.py forms. Used by __init__
    def dropdown_options(self):
        jarenDB = model.get_years_available()

        options = {}
        options['empty'] = [ ('', '')]
        options['all'] = [ ('*','! ALL !') ]
        options['years'] = zip(jarenDB, jarenDB)
        options['tables'] = config['mysql']['tables']['regels'].items()

        options['empty_years_all'] = options['empty'] + options['years'] + options['all']

        options['empty_tables'] = options['empty'] + options['tables']
        options['empty_tables_all'] = options['empty'] + options['tables'] + options['all']

        return options


# Simple webpage for messages/forms
class Simple(Webpage):
    def __init__(self, userHash, title, msg, redirect=''):
        Webpage.__init__(self, userHash, None)

        #subclass specific
        self.title = title
        self.msg = msg
        self.redirect = redirect
        self.form_redirect = form.Form(
                form.Button('ok', value='redirect')
        )


    def render_body(self):
        if self.redirect:
            self.form = self.form_redirect
        else:
            self.form = ''

        redirect = '/%s/%s' % (self.redirect, self.userHash)
        self.body = self.mainRender.simple(self.title, self.msg, self.form, redirect)

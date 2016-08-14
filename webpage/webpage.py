import web
from web import form
from config import config
import model

# Mother class for all webpages
class Webpage(object):
    def __init__(self, userHash, static=False):
        self.userHash = userHash
        self.static = static
        self.mainRender = web.template.render('webpage/templates/', cache=False) #in init cause subclasses might also access it
        print 'WARNING DEBUG CODE STILL ON '
        print 'WARNING DEBUG CODE STILL ON '
        print 'WARNING DEBUG CODE STILL ON '

        # should be set in the subclass
        self.title = None
        self.module = None
        self.webrender = None
        self.breadCrum = None #list of dict items (keys: title, ulr, class:active)

    def render(self):
        self.render_body() #Start with rendering subclass in case it sets breadcrums etc.
#TODO cache renderd page and check if we can serve that
        navbar = self.mainRender.navbar(self.userHash, self.breadCrum, self.groups)
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

# Simple webpage for messages/forms
class Simple(Webpage):
    def __init__(self, userHash):
        Webpage.__init__(self, userHash)

        #subclass specific
        self.title = ''
        self.msg = ''
        self.redirect = ''
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

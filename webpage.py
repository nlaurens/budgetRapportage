import web
from web import form
import model
from config import config

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


    def render(self):
#TODO cache renderd page and check if we can serve that
        self.render_body()
        return self.mainRender.page(self.title, self.body)

    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError

    #used for creating links in the submodule
    def base_url(self):
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

        self.body = self.mainRender.simple(self.title, self.msg, self.form)

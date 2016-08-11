import web
import model
from config import config

# Mother class for all webpages
class Webpage(object):
    def __init__(self, userHash, params, static=False):
        self.userHash = userHash
        self.params = params
        self.static = static
        self.mainRender = web.template.render('templates/', cache=False) #in init cause subclasses might also access it
        self.dropDownOptions = self.dropdown_options()

        # should be set in the subclass
        self.title = None
        self.module = None
        self.webrender = None

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


    def render(self):
#TODO cache renderd page and check if we can serve that
        self.render_body()
        return self.mainRender.page(self.title, self.body)


    def base_url(self):
        return ('/%s/%s' % (self.module, self.userHash))


    # Should be implemented by subclass
    def render_body(self):
        raise NotImplementedError


# Simple webpage for messages/forms
class Simple(Webpage):
    def __init__(self, userHash, title, msg, form=''):
        Webpage.__init__(self, userHash, None)

        #subclass specific
        self.title = title
        self.msg = msg
        self.form = form


    def render_body(self):
        self.body = self.mainRender.simple(self.title, self.msg, self.form)

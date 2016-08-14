from controller import Controller
import webpage
from budget import run_tests

class Admin(Controller):
    def process_sub(self, userHash):
        page = webpage.Simple(userHash)
        self.set_page_attr(page)
#TODO
        page.msg = run_tests()
        return page.msg
        #page = webadmin.Admin(userHash, 'formAction') # on post~
        return page.render()

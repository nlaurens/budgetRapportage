from controller import Controller
import webpage
from budget import run_tests as budget_run_tests

class Admin(Controller):
    def process_sub(self, userHash):
        page = webpage.Admin(userHash)
        self.set_page_attr(page)
#TODO
        page.msg = ['Welcome to the Admin panel']
        page.msg.extend(budget_run_tests())

        # Handle posted forms
        if self.caller == 'POST':
            (validForm, msg) = page.parse_forms()
            if validForm:
                page = webpage.Simple(userHash)
                page.set_page_attr(page)
                page.title = 'Admin Panel results'
                page.msg = msg 
                return page.render()

#GET
        return page.msg

        return page.msg

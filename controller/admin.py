from controller import Controller
import webpage

class Admin(Controller):
    def process_sub(self, userHash):
        page = webadmin.Simple(userHash)
        page.SAPupdate = self.SAPupdate
        page.groups = self.groups
#TODO
        page = webadmin.Admin(userHash, 'formAction') # on post~
        return page.render()

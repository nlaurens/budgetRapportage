from controller import Controller
import webpage

class Index(Controller):
    def process_sub(self, userHash):
        page = webpage.Simple(userHash)
        page.SAPupdate = self.SAPupdate
        page.groups = self.groups

        page.title = 'Welcome'
        page.msg = 'Make a selection from the menu above.'
        return page.render()

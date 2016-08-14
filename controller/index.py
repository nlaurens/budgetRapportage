from controller import Controller
import webpage

class Index(Controller):
    def process_sub(self, userHash):
        page = webpage.Simple(userHash)
        page.set_title('Welcome')
        page.set_msg('Make a selection from the menu above.')
        page.set_SAPupdate(self.SAPupdate)
        return page.render()

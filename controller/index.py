from controller import Controller
import webpage

class Index(Controller):
    def process_sub(self, userHash):
        page = webpage.Simple(userHash)
        self.set_page_attr(page)
        page.title = 'Welcome'
        page.msg = 'Make a selection from the menu above.'
        return page.render()

from controller import Controller
class Index(Controller):
    def process_sub(self, userHash):
        print 'process_sub'
        return 'this is the index'
        page = webpage.Simple(userHash)
        page.set_title('Welcome')
        page.set_msg('Make a selection from the menu above.')
        return page.render()

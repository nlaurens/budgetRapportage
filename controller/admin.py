from controller import Controller
class Admin(Controller):
    def process_sub(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'admin')
        page = webadmin.Admin(userHash)
#TODO
        page = webadmin.Admin(userHash, 'formAction') # on post~
        return page.render()

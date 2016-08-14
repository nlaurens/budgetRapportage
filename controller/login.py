from controller import Controller
class Login(Controller):
    def process_sub(self, userHash):
        auth_block_by_ip()
        page = webaccess.Login(userHash)
        return page.render()

from controller import Controller
class Logout(Controller)
    def process_sub(self, userHash):
        auth_block_by_ip()
        session.logged_in = False
        page = webpage.Simple(userHash, 'Logout', 'You have been logged out')
        return page.render()

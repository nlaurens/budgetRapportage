from controller import Controller
class View(Controller):
    def process_sub(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'view')
        page = webview.View(userHash)
        return page.render()

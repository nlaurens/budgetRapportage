class View:
    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'view')
        page = webview.View(userHash)
        return page.render()


    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'view')
        page = webview.View(userHash)
        return page.render()

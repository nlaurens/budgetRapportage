class Admin:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'admin')
        page = webadmin.Admin(userHash)
        return page.render()

    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'admin')
        page = webadmin.Admin(userHash, 'formAction')
        return page.render()

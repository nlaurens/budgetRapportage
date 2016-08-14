class Login:
    def GET(self, userHash):
        auth_block_by_ip()
        page = webaccess.Login(userHash)
        return page.render()

    def POST(self, userHash):
        auth_block_by_ip()
        page = webaccess.Login(userHash)
        page.parse_form(session) #will redirect on success
        return page.render()

class Index:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'index')
        page = webpage.Simple(userHash)
        page.set_title('Welcome')
        page.set_msg('Make a selection from the menu above.')
        return page.render()

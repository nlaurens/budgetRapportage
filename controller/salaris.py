class Salaris:
    def process_sub(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'salaris')
        page = websalaris.Salaris(userHash)
        return page.render()

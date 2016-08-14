class Report:
    def GET(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'report')
        page = webreport.Report(userHash)
        return page.render()


    def POST(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'report')
        page = webreport.Report(userHash)
        return page.render()

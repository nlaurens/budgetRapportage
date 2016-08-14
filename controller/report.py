from controller import Controller
class Report(Controller):
    def process_sub(self, userHash):
        auth_block_by_ip()
        auth_login(session, userHash, 'report')
        page = webreport.Report(userHash)
        return page.render()

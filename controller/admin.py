from controller import Controller
import webpage
from budget import run_tests as budget_run_tests

class Admin(Controller):
    def process_sub(self, userHash):
        page = webpage.Admin(userHash, self.dropdown_options())
        self.set_page_attr(page)
#TODO
        page.msg = ['Welcome to the Admin panel']
        page.msg.extend(budget_run_tests())

        # Handle posted forms
        if self.caller == 'POST':
            (validForm, msg) = page.parse_forms()
            if validForm:
                page = webpage.Simple(userHash)
                page.set_page_attr(page)
                page.title = 'Admin Panel results'
                page.msg = msg 
                return page.render()

        #GET
#TODO coppelen aan config.user
        page.authList = model.get_auth_list(config['salt'])
        page.dbStatus = self.db_status()

        return page.msg

    def db_status(self):
        #construct dict with total regels per table
        yearsFound = set()
        regelCount = {}
        totals = {}
        totals['total'] = 0

        for table in config["mysql"]["tables"]["regels"]:
            regelCount[table] = {}
            if model.check_table_exists(table):
                regelCount[table][0] = "OK"
                years = model.get_years_available()
                yearsFound = yearsFound.union(years)
                for year in sorted(list(years)):
                    regelCount[table][year] = model.count_regels(int(year), table)
                    if year not in totals:
                        totals[year] = regelCount[table][year]
                        totals['total'] += regelCount[table][year]
                    else:
                        totals[year] += regelCount[table][year]
                        totals['total'] += regelCount[table][year]
            else:
                regelCount[table][0] = "Not found"

        # create vars for render
        tableNames = regelCount.keys()
        regelsHeaders= ['table', 'status' ]
        for year in sorted(list(yearsFound)):
            regelsHeaders.append(str(year))

        regelsBody = []
        for table in tableNames:
            regel = [table, regelCount[table][0]]
            for year in sorted(list(yearsFound)):
                regel.append(regelCount[table][year])
            regelsBody.append(regel)

        regelsTotal = ['Total', totals['total']]
        for year in sorted(list(yearsFound)):
            regelsTotal.append(totals[year])

        return [regelsHeaders, regelsBody, regelsTotal]



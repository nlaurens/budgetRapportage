"""
TODO
- opmaak admin form descr (nu nog vaak descr = name)
"""
import web
from web import form

import os
from xlsx2csv import Xlsx2csv
import csv
import datetime
import functions

import webpage
from webpage import Webpage

class Admin(Webpage):
    def __init__(self, userHash, subpage='main'):
        Webpage.__init__(self, userHash)

        #subclass specific
        self.title = 'Admin Panel'
        self.module = 'admin'
        self.subpage = subpage
        self.webrender = web.template.render('templates/admin/')

        #Admin specific
        self.msg = ['Welcome to the Admin panel']

        #Forms
        self.form_remove_regels = form.Form(
            form.Dropdown('year', self.dropDownOptions['empty_years_all'],
                form.notnull, description='Year to remove: '),
            form.Dropdown('table', self.dropDownOptions['empty_tables_all'],
                form.notnull, description='Table to remove from: '),
            form.Button('submit', value='removeRegels')
        )
        self.form_upload_regels = form.Form(
                form.File(name='upload1'),
                form.Dropdown('type1', self.dropDownOptions['empty_tables']),
                form.File(name='upload2'),
                form.Dropdown('type2', self.dropDownOptions['empty_tables']),
                form.File('upload3'),
                form.Dropdown('type3', self.dropDownOptions['empty_tables']),
                form.File('upload4'),
                form.Dropdown('type4', self.dropDownOptions['empty_tables']),
                form.File('upload5'),
                form.Dropdown('type5', self.dropDownOptions['empty_tables']),
                form.Button('submit', value='uploadRegels')
        )
        self.form_update_sap_date = form.Form(
                form.Textbox('sapdate', form.notnull, value=model.last_update(),
                    description='Date last SAP regels are uploaded'),
                form.Button('submit', value='updateSapDate')
        )
        self.form_rebuild_graphs = form.Form(
                form.Textbox('target', form.notnull, description='Order/groep/*'),
                form.Dropdown('year', self.dropDownOptions['empty_years_all'], form.notnull),
                form.Button('submit', value='rebuildGraphs')
        )


    def render_body(self):
        if self.subpage == 'main':
            self.render_body_main()
        elif self.subpage == 'formAction':
            (validForm, msg) = self.parse_forms()
            if validForm:
                page = webpage.Simple(self.userHash, 'Admin', msg, 'admin')
                page.render()
                self.body = page.body # we don't need the header/footer
            else:
                self.render_body_main()
        else:
            self.body = 'webadmin subpage %s unknown' % self.subpage


    def render_body_main(self):
        testResults = self.run_tests()
        self.msg.extend(testResults)

        rendered = {}
        rendered['userAccess'] = self.webrender.user_access(model.get_auth_list(config['salt']) )
        rendered['dbStatus'] = self.render_db_status()

        rendered['forms'] = []
        rendered['forms'].append(self.webrender.form('Remove Regels From DB', self.form_remove_regels))
        rendered['forms'].append(self.webrender.form('Upload Regels to DB', self.form_upload_regels))
        rendered['forms'].append(self.webrender.form('Update last SAP-update-date', self.form_update_sap_date))
        rendered['forms'].append(self.webrender.form('Update Graphs', self.form_rebuild_graphs))

        self.body = self.webrender.admin(self.msg, rendered)

    def render_db_status(self):
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

        return self.webrender.db_status(regelsHeaders, regelsBody, regelsTotal)


    def run_tests(self):
        msg = ['Running tests']
        success, testMsg = tests.ks_missing_in_report()
        if success:
            msg.append('* ks-test: Pass')
        else:
            msg.append('WARNING KS THAT ARE NOT IN REPORTS FOUND IN DB!')
            msg.extend(testMsg)
        return msg


    def parse_forms(self):
        validForm = False
        msg = ['Parsing forms']

        formUsed = web.input()['submit']
        if formUsed == 'removeRegels' and self.form_remove_regels.validates():
            msg.extend( self.parse_remove_regels() )
            validForm = True

        if formUsed == 'uploadRegels' and self.form_upload_regels.validates():
            msg.extend(self.parse_upload_form())
            validForm = True

        if formUsed == 'updateSapDate' and self.form_update_sap_date.validates():
            msg.append('Updating last sap update date')
            model.last_update(self.form_update_sap_date['sapdate'].value)
            validForm = True

        if formUsed =='rebuildGraphs' and self.form_rebuild_graphs.validates():
            msg.extend(self.parse_rebuild_graphs())
            validForm = True

        return (validForm, msg)


    def parse_remove_regels(self):
        msg = ['Removing regels from DB']
        jaar = self.form_remove_regels['year'].value
        if jaar == '*':
            jaar = '%'
        else:
            jaar = int(jaar)

        table = self.form_remove_regels['table'].value
        if table == '':
            msg.append("No valid table selected")
            return msg

        msg.append("Purging year %s" % jaar)
        msg.append("From table  %s" % table)
        if table == '*':
            aantalWeg = model.delete_regels(jaar)
        else:
            aantalWeg = model.delete_regels(jaar, tableNames=[table])
        msg.append("Deleted %s rows" % aantalWeg)

        return msg


    def parse_rebuild_graphs(self):
        msg = ['Parsing rebuild graph']
#TODO security op deze input, jaar = int tussen x en y. target = string
        jaar = self.form_rebuild_graphs['year'].value
        target = self.form_rebuild_graphs['target'].value

        msg.append("running: $python graph.py %s %s" % (target, jaar))
#TODO SOMEDAY fire proccess in sep. thread, graph.py write a log (clean everytime it starts), and webadmin poll if there is such a log running (report using msg)
        os.system("python graph.py %s %s" % (target, jaar))
        return msg


    def parse_upload_form(self):
        msg = ['Start parsing of upload form']
        fileHandle = web.input(upload1={}, upload2={}, upload3={}, upload4={}, upload5={})
        uploads = []
        for i in range(1,6):
            try:
                fileHandle = eval("fileHandle.upload%s" % i)
            except:
                fileHandle = None
            table = eval("self.form_upload_regels['type%s'].value" % i)

            if fileHandle != None and table in config['mysql']['tables']['regels'].values():
                msg.extend(self.upload_and_process_file(table, fileHandle))

        return msg

    def upload_and_process_file(self, table, fileHandle):
        msg = ['Starting upload']
        allowed = ['.xlsx']
        msg.append('Uploading file.')
        succes_upload = False
        pwd, filenamefull = os.path.split(fileHandle.filename)
        filename, extension = os.path.splitext(filenamefull)
        if extension in allowed:
            fout = open(table+'.xlsx','wb')
            fout.write(fileHandle.file.read())
            fout.close()
            succes_upload = True

        if not succes_upload:
            msg.append('upload failed!')
            return msg
        msg.append('upload succes')

        msg.append('Preparing to process data for table: ' + table)
        xlsx2csv = Xlsx2csv(table+'.xlsx')
        xlsx2csv.convert(str(table)+'.csv', sheetid=1)
        if not os.path.isfile(table+'.csv'):
            msg.append('xlsx to csv convertion failed')
            return msg
        msg.append('xlsx to csv convertion succes')

        if model.check_table_exists(table):
            table_backup = table + datetime.datetime.now().strftime("%Y%m%d%H%M-%f")
            msg.append('Copying '+table+' to ' + table_backup)
            if not model.copy_table(table, table_backup):
                msg.append('Copying table failed!')
                return msg
            msg.append('Copying table succes')

        msg.append('Reading headers from CSV')
        f = open(table+'.csv', 'rb')
        reader = csv.reader(f)
        headers = reader.next()
        header_map = {y:x for x,y in config["SAPkeys"][table].iteritems()}
        fields = []
        for header in headers:
            if header in header_map:
                fields.append(header_map[header])
            else:
                msg.append('Unknown field in excel: ' + header)
                msg.append('Import stopped!')
                return msg

        for attribute, SAPkey in config["SAPkeys"][table].iteritems():
            if attribute not in fields:
                msg.append('Required field not in excel: ' + attribute)
                return msg

        if not model.check_table_exists(table):
            msg.append('Creating new table using headers')
            model.create_table(table, fields)
        else:
            msg.append('Table already exists, add regels to it.')


        # Fill table from CSV
        msg.append('Inserting data into table')
        rows = []
        rownumber = 1
        for row in reader:
            row_empty_replaced = [element or '0' for element in row]
            if row_empty_replaced != row:
                empty_indexes = [i for i, item in enumerate(row) if item == '']
                for index in empty_indexes:
                    msg.append('WARNING empty %s in row #(%s)' %(fields[index],rownumber) )
            rows.append(dict(zip(fields, row_empty_replaced)))
            rownumber +=1
        f.close()

        model.insert_into_table(table, rows)

        # clean up
        msg.append('Cleaning up files')
        #os.remove(table+'.xlsx') # BUG.. xlsx2csv seems to block the file handle.
        os.remove(table+'.csv')
        msg.append('')

        return msg


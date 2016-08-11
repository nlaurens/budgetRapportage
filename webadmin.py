"""
TODO

"""
import web
from web import form

import model
import os
from xlsx2csv import Xlsx2csv
import csv
import datetime
import tests
import functions

from webpage import Webpage
from config import config

#TODO get all from params not web.input

class Admin(Webpage):
    def __init__(self, userHash, params):
        Webpage.__init__(self, userHash, params)

        #subclass specific
        self.title = 'Admin Panel'
        self.module = 'admin'
        self.webrender = web.template.render('templates/admin/')

        #Admin specific
        self.msg = ['Welcome to the Admin panel']

#DAN CLASSE HIERHEEN EN IMPORTEREN IN SERVER
        #Forms
        self.form_remove_regels = form.Form(
            form.Dropdown('year', self.dropDownOptions['empty_years_all'], 
                form.notnull, description='Year to remove: '),
            form.Dropdown('table', self.dropDownOptions['empty_tables_all'],
                form.notnull, description='Table to remove from: '),
        )
        self.form_upload_regels = form.Form(
                form.File('myfile1'),
                form.Dropdown('Type1', self.dropDownOptions['empty_tables']),
                form.File('myfile2'),
                form.Dropdown('Type2', self.dropDownOptions['empty_tables']),
                form.File('myfile3'),
                form.Dropdown('Type3', self.dropDownOptions['empty_tables']),
                form.File('myfile4'),
                form.Dropdown('Type4', self.dropDownOptions['empty_tables']),
                form.File('myfile5'),
                form.Dropdown('Type5', self.dropDownOptions['empty_tables']),
            )
        self.form_update_sap_date = form.Form(
                form.Textbox('Sapdate:', value=model.last_update()),
            )
        self.form_rebuild_graphs = form.Form(
                form.Textbox('target', description='Order/groep/*'),
                form.Dropdown('Year', self.dropDownOptions['empty_years_all']),
            )


    def render_body(self):
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
        form = self.form_remove_regels()
        if form.validates():
            self.msg.append('dummy remove regels parse')

        return

        #handling of the post action:
        if 'Update' in web.input():
            msg = ['Updating last sap update date']
            model.last_update(web.input()['Sapdate'])
            msg.append('DONE')
        if 'Upload data' in web.input():
            msg = webadmin.parse_upload_form()
        if 'Refresh Graphs' in web.input():
            msg = webadmin.parse_updateGraphs()
        if 'Purge year from regels' in web.input():
            msg = webadmin.parse_purgeRegelsForm()

    def parse_purgeRegelsForm(self):
        msg = ["Purging year from regels..."]
        jaar = web.input()['Year']
        if web.input()['Year'] == '*':
            jaar = '%' 
        else:
            try:
                jaar = int(jaar)
            except:
                msg.append("No valid year selected")
                return msg

        table = web.input()['Table']
        if table == '':
            msg.append("No valid table selected")
            return msg


        msg.append("From table  %s" % table)
        msg.append("Purging year %s" % jaar)
        if table == '*':
            aantalWeg = model.delete_regels(jaar)
        else:
            aantalWeg = model.delete_regels(jaar, tableNames=[table])
        msg.append("Deleted %s rows" % aantalWeg)
        return msg


    def parse_updateGraphs(self):
        msg = ['Parsing rebuild graph']

        target = web.input()['target']
        jaar = web.input()['Year']
#TODO duplicate code below. perhaps make a 'year' checker?
        if web.input()['Year'] == '%':
            jaar = '*'
        else:
            try:
                jaar = int(jaar)
            except:
                msg.append("No valid year selected")
                return msg

        msg.append("running: $python graph.py %s %s" % (target, jaar))
#TODO SOMEDAY fire proccess in sep. thread, graph.py write a log (clean everytime it starts), and webadmin poll if there is such a log running (report using msg)
        os.system("python graph.py %s %s" % (target, jaar))
        return msg


    def parse_upload_form(self):
        msg = ['Start parsing of upload form']
        # try each upload
#TODO make this iterable.. web.input(myfile1).myfile1 is the problem.
        fileHandle = web.input(myfile1={}).myfile1
        table = web.input()['Type1']
        msg = upload_and_process_file('myfile1', table, fileHandle, msg)

        fileHandle = web.input(myfile2={}).myfile2
        table = web.input()['Type2']
        msg = upload_and_process_file('myfile2', table, fileHandle, msg)

        fileHandle = web.input(myfile3={}).myfile3
        table = web.input()['Type3']
        msg = upload_and_process_file('myfile3', table, fileHandle, msg)

        fileHandle = web.input(myfile4={}).myfile4
        table = web.input()['Type4']
        msg = upload_and_process_file('myfile4', table, fileHandle, msg)

        fileHandle = web.input(myfile5={}).myfile5
        table = web.input()['Type5']
        msg = upload_and_process_file('myfile5', table, fileHandle, msg)

        return msg

    def upload_and_process_file(self, fileHandleName, table, fileHandle, msg):
        table_allowed = False
        if table in config['mysql']['tables']['regels'].values():
            table_allowed = True

        if not table_allowed:
            msg.append('Type not selected!')
            return msg

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


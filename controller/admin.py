from xlsx2csv import Xlsx2csv
import csv
import datetime
import os

from controller import Controller
import web
from web import form
import model.regels
import model.functions

class Admin(Controller):
    def __init__(self):
        Controller.__init__(self)

        #subclass specific
        self.title = 'Admin Panel'
        self.module = 'admin'
        self.webrender = web.template.render('webpages/admin/')

        #Forms
        dropDownOptions = self.dropdown_options()

        self.form_remove_regels = form.Form(
            form.Dropdown('year', dropDownOptions['empty_years_all'],
                form.notnull, description='Year to remove: '),
            form.Dropdown('table', dropDownOptions['empty_tables_all'],
                form.notnull, description='Table to remove from: '),
            form.Button('submit', value='removeRegels')
        )
        self.form_upload_regels = form.Form(
                form.File(name='upload1'),
                form.Dropdown('type1', dropDownOptions['empty_tables']),
                form.File(name='upload2'),
                form.Dropdown('type2', dropDownOptions['empty_tables']),
                form.File('upload3'),
                form.Dropdown('type3', dropDownOptions['empty_tables']),
                form.File('upload4'),
                form.Dropdown('type4', dropDownOptions['empty_tables']),
                form.File('upload5'),
                form.Dropdown('type5', dropDownOptions['empty_tables']),
                form.Button('submit', value='uploadRegels')
        )
        self.form_update_sap_date = form.Form(
                form.Textbox('sapdate', form.notnull, value=self.SAPupdate,
                    description='Date last SAP regels are uploaded'),
                form.Button('submit', value='updateSapDate')
        )
        self.form_rebuild_graphs = form.Form(
                form.Textbox('target', form.notnull, description='Order/groep/*'),
                form.Dropdown('year', dropDownOptions['empty_years_all'], form.notnull),
                form.Button('submit', value='rebuildGraphs')
        )

    def process_sub(self):
        # Handle posted forms
        if self.callType == 'POST':
            (validForm, msg) = self.parse_forms()
            if validForm:
                self.title = 'Admin Panel Results'
                self.msg = msg 
                self.redirect = 'admin'
                self.body = self.render_simple()
                return # prevent Get page from rendering

        # Display admin page on GET or invalid form post
        self.msg = ['Welcome to the Admin panel']
        self.msg.extend(self.run_tests())

#TODO coppelen aan config.user
        self.authList = '' #model.db.get_users()

        rendered = {}
        rendered['userAccess'] = self.webrender.user_access(self.authList)
        rendered['dbStatus'] = self.webrender.db_status(self.db_status())

        rendered['forms'] = []
        rendered['forms'].append(self.webrender.form('Remove Regels From DB', self.form_remove_regels))
        rendered['forms'].append(self.webrender.form('Upload Regels to DB', self.form_upload_regels))
        rendered['forms'].append(self.webrender.form('Update last SAP-update-date', self.form_update_sap_date))
        rendered['forms'].append(self.webrender.form('Update Graphs', self.form_rebuild_graphs))

        self.body = self.webrender.admin(self.msg, rendered)

    def db_status(self):
        #construct dict with total regels per table
        db_status = {}

        regel_count = model.regels.count()
        tableNames = regel_count.keys()
        years = model.regels.years()


        # create vars for render
        db_status['headers'] = ['table', 'status' ]
        for year in years:
            db_status['headers'].append(str(year))

        db_status['body'] = []
        for table in tableNames:
            if model.regels.check_table_exists(table):
                regel = [table, '']
            else:
                regel = [table, 'ERROR']
            for year in years:
                regel.append(regel_count[table][year])
            db_status['body'].append(regel)

        db_status['totals'] = ['Total', '']
        for year in years:
            total = 0
            for table in tableNames:
                total += int(regel_count[table][year])
            db_status['totals'].append(total)

        return db_status

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
            model.regels.last_update(self.form_update_sap_date['sapdate'].value)
            validForm = True

        if formUsed =='rebuildGraphs' and self.form_rebuild_graphs.validates():
            msg.extend(self.parse_rebuild_graphs())
            validForm = True

        return (validForm, msg)


    def parse_remove_regels(self):
        msg = ['Removing regels from DB']
        year = self.form_remove_regels['year'].value
        table = self.form_remove_regels['table'].value

        msg.append("Purging year %s" % year)
        msg.append("From table  %s" % table)

        if table == '':
            msg.append("No valid table selected")
            return msg
        elif table == '*':
            tableNames = []
        else:
            tableNames = [table]

        if year == '':
            msg.append("No valid year selected")
            return msg
        elif year == '*':
            years = []
        else:
            years = [year]

        deleted = model.regels.delete(years=years, tableNames=tableNames)
        msg.append("Deleted %s rows" % deleted)

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
        fileHandles = web.input(upload1={}, upload2={}, upload3={}, upload4={}, upload5={})
        uploads = []
        for i in range(1,6):
            try:
                fileHandle = eval("fileHandles.upload%s" % i)
            except:
                fileHandle = None
            table = eval("self.form_upload_regels['type%s'].value" % i)

            if fileHandle != None and table in self.config['mysql']['tables']['regels'].values():
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

        msg.append('Reading headers from CSV')
        f = open(table+'.csv', 'rb')
        reader = csv.reader(f)
        headers = reader.next()
        header_map = {y:x for x,y in self.config["SAPkeys"][table].iteritems()}

        fields = []
        for header in headers:
            if header in header_map:
                fields.append(header_map[header])
            else:
                msg.append('Unknown field in excel: ' + header)
                msg.append('Import stopped!')
                return msg

        for attribute, SAPkey in self.config["SAPkeys"][table].iteritems():
            if attribute not in fields:
                msg.append('Required field not in excel: ' + attribute)
                return msg

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

        model.regels.add(table, fields, rows)

        # clean up
        msg.append('Cleaning up files')
        
        del xlsx2csv 
        os.remove(table+'.xlsx') # BUG.. xlsx2csv seems to block the file handle.
        os.remove(table+'.csv')
        msg.append('')

        return msg

    def run_tests(self):
        success = False
        msg = [ 'nothing implmented' ]

        return (success, msg)

# Test to see if there are regels containing ks that are not
# in a report (and therefore would not show up).
    def test_ks_missing_in_report():
        msg = []
        success = True
        ksDB = model.get_kosten_soorten()

        # loop over all kostensoortgroepen
        for ksGroepName in model.loadKSgroepen().keys():
            root = GrootBoek.load(ksGroepName)
            ksGroep = root.get_ks_recursive()
            for ks in ksDB:
                if ks not in ksGroep:
                    success = False
                    msg.append('WARNING kostensoort %s appears in DB but is not included in report %s' % (ks, ksGroepName))

        return (success, msg)


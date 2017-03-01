from xlsx2csv import Xlsx2csv
import csv
import os
import tempfile

from controller import Controller
import web
from web import form
import model.regels
import model.ksgroup
import model.orders

from config import config
from model.functions import count_tables_other

class Admin(Controller):
    def __init__(self):
        Controller.__init__(self)

        # subclass specific
        self.title = 'Admin Panel'
        self.module = 'admin'
        self.webrender = web.template.render('webpages/admin/')
        self.lastperiode = model.regels.last_periode()  # gives subclass__init__ access
        
        # Forms
        drop_down_options = self.dropdown_options()

        self.form_remove_regels = form.Form(
            form.Dropdown('year', drop_down_options['empty_years_all'],
                          form.notnull, description='Year to remove: '),
            form.Dropdown('table', drop_down_options['empty_tables_all'],
                          form.notnull, description='Table to remove from: '),
            form.Button('submit', value='removeRegels')
        )
        self.form_upload = form.Form(
                form.File(name='upload1'),
                form.Dropdown('type1', drop_down_options['empty_tables']),
                form.File(name='upload2'),
                form.Dropdown('type2', drop_down_options['empty_tables']),
                form.File('upload3'),
                form.Dropdown('type3', drop_down_options['empty_tables']),
                form.File('upload4'),
                form.Dropdown('type4', drop_down_options['empty_tables']),
                form.File('upload5'),
                form.Dropdown('type5', drop_down_options['empty_tables']),
                form.Button('submit', value='uploadRegels')
        )
        self.form_update_sap = form.Form(
                form.Textbox('sapdate', form.notnull, value=self.SAPupdate,
                             description='Date last SAP regels are uploaded'),
                form.Dropdown('sapperiode', drop_down_options['months'], value=self.lastperiode,
                               description='Last periode obligo/salarissen updated'),
                form.Button('submit', value='updateSapDates')
        )
        self.form_rebuild_graphs = form.Form(
                form.Textbox('target', form.notnull, description='Order/groep/*'),
                form.Dropdown('year', drop_down_options['empty_years_all'], form.notnull),
                form.Button('submit', value='rebuildGraphs')
        )

    def process_sub(self):
        # Handle posted forms
        if self.callType == 'POST':
            (valid_form, msg) = self.parse_forms()
            if valid_form:
                self.title = 'Admin Panel Results'
                self.msg = msg
                self.redirect = 'admin'
                self.body = self.render_simple()
                return  # prevent Get page from rendering

        # Display admin page on GET or invalid form post
        self.msg = ['Welcome to the Admin panel']
        self.msg.extend(self.run_tests())

# TODO coppelen aan config.user
        self.authList = ''  # model.db.get_users()

        rendered = {}
        rendered['userAccess'] = self.webrender.user_access(self.authList)
        status_regels, status_other_tables = self.db_status()
        rendered['dbStatus'] = self.webrender.db_status(status_regels, status_other_tables)

        rendered['forms'] = []
        rendered['forms'].append(self.webrender.form('Remove Regels From DB', self.form_remove_regels))
        rendered['forms'].append(self.webrender.form('Upload File', self.form_upload))
        rendered['forms'].append(self.webrender.form('Update last SAP-update-date', self.form_update_sap))
        rendered['forms'].append(self.webrender.form('Update Graphs', self.form_rebuild_graphs))

        self.body = self.webrender.admin(self.msg, rendered)

    def db_status(self):
        # construct dict with total regels per table
        status_regels = {}

        regel_count = model.regels.count()
        table_names = regel_count.keys()
        years = model.regels.years()

        # create vars for render
        status_regels['headers'] = ['table', 'status']
        for year in years:
            status_regels['headers'].append(str(year))

        status_regels['body'] = []
        for table in table_names:
            if model.regels.check_table_exists(table):
                regel = [table, 'OK']
            else:
                regel = [table, 'ERROR']
            for year in years:
                regel.append(regel_count[table][year])
            status_regels['body'].append(regel)

        status_regels['totals'] = ['Total', '']
        for year in years:
            total = 0
            for table in table_names:
                total += int(regel_count[table][year])
            status_regels['totals'].append(total)

        status_other_tables = {}
        status_other_tables['headers'] = ['table', 'status', '# entries']
        status_other_tables['body'] = []

        # Stick to all the tables from the config that are not regels
        for table, count in count_tables_other().iteritems():
            status = 'OK'
            if count == -1:
                status = 'ERROR'
                count = ''
            status_other_tables['body'].append([table, status, count])

        return status_regels, status_other_tables

    def parse_forms(self):
        valid_form = False
        msg = ['Parsing forms']

        form_used = web.input()['submit']
        if form_used == 'removeRegels' and self.form_remove_regels.validates():
            msg.extend(self.parse_remove_regels())
            valid_form = True

        if form_used == 'uploadRegels' and self.form_upload.validates():
            msg.extend(self.parse_upload_form())
            valid_form = True

        if form_used == 'updateSapDates' and self.form_update_sap.validates():
            msg.append('Updating last sap update date')
            model.regels.last_update(self.form_update_sap['sapdate'].value)
            model.regels.last_periode(self.form_update_sap['sapperiode'].value)
            valid_form = True

        if form_used == 'rebuildGraphs' and self.form_rebuild_graphs.validates():
            msg.extend(self.parse_rebuild_graphs())
            valid_form = True

        return valid_form, msg

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
            table_names = []
        else:
            table_names = [table]

        if year == '':
            msg.append("No valid year selected")
            return msg
        elif year == '*':
            years = []
        else:
            years = [year]

        deleted = model.regels.delete(years_delete=years, table_names_delete=table_names)
        msg.append("Deleted %s rows" % deleted)

        return msg

    def parse_rebuild_graphs(self):
        msg = ['Parsing rebuild graph']
# TODO security op deze input, jaar = int tussen x en y. target = string
        jaar = self.form_rebuild_graphs['year'].value
        target = self.form_rebuild_graphs['target'].value

        msg.append("running: $python graph.py %s %s" % (target, jaar))
# TODO SOMEDAY fire proccess in sep. thread, graph.py write a log (clean everytime it starts), and webadmin poll if there is such a log running (report using msg)
        os.system("python graph.py %s %s" % (target, jaar))
        return msg

    def parse_upload_form(self):
        msg = ['Start parsing of upload form']
        file_handles = web.input(upload1={}, upload2={}, upload3={}, upload4={}, upload5={})
        uploads = []
        for i in range(1, 6):
            try:
                file_handle = eval("file_handles.upload%s" % i)
            except Exception:
                file_handle = None
            table = eval("self.form_upload['type%s'].value" % i)

            if file_handle is not None and table in self.config['mysql']['tables']['regels'].keys():
                msg_read_xlsx, fields, rows = self.read_xlsx(file_handle, table)
                msg.extend(msg_read_xlsx)
                if fields is not None and rows is not None:
                    model.regels.add(table, fields, rows)

            if file_handle is not None and table == 'orderlijst':
                msg_read_xlsx, fields, rows = self.read_xlsx(file_handle, table)
                msg.extend(msg_read_xlsx)
                if fields is not None and rows is not None:
                    #TODO add 'clear/inserting in db' msg to msg quque
                    model.orders.clear()  # every upload should be the whole list
                    model.orders.add(fields, rows)
        return msg

    # Uploads and reads xlsx file
    # Returns fields and rows of the excel
    def read_xlsx(self, file_handle, table):
        msg = ['Starting uploading file']
        fields = []
        rows = []

        allowed = ['.xlsx']
        msg.append('Uploading file.')
        pwd, filenamefull = os.path.split(file_handle.filename)
        filename, extension = os.path.splitext(filenamefull)
        if extension not in allowed:
            msg.append('extension not allowed!')
            return msg

        with tempfile.NamedTemporaryFile(delete=False) as tmpxlsx:
            tmpxlsx.write(file_handle.file.read())
            tmpxlsx.flush()
            msg.append('upload succes')

            msg.append('Preparing to convert xlsx to csv')
            with tempfile.NamedTemporaryFile(delete=False) as tmpcsv:
                xlsx2csv = Xlsx2csv(tmpxlsx.name)
                xlsx2csv.convert(tmpcsv.name, sheetid=1)
                if not os.path.isfile(tmpcsv.name):
                    msg.append('xlsx to csv convertion failed')
                    return msg, None, None
                msg.append('xlsx to csv convertion succes')

                msg.append('Reading headers from CSV')
                f = open(tmpcsv.name, 'rb')
                reader = csv.reader(f)
                headers = reader.next()
                header_map = {y: x for x ,y in self.config["SAPkeys"][table].iteritems()}

                fields = []
                for header in headers:
                    if header in header_map:
                        fields.append(header_map[header])
                    else:
                        msg.append('Unknown field in excel: ' + header)
                        msg.append('Import stopped!')
                        return msg, None, None

                for attribute, SAPkey in self.config["SAPkeys"][table].iteritems():
                    if attribute not in fields:
                        msg.append('Required field not in excel: ' + attribute)
                        return msg, None, None

                # Fill table from CSV
                msg.append('Inserting data into table')
                rows = []
                rownumber = 1
                for row in reader:
                    row_empty_replaced = [element or '0' for element in row]
                    if row_empty_replaced != row:
                        empty_indexes = [i for i, item in enumerate(row) if item == '']
                        for index in empty_indexes:
                            msg.append('WARNING empty %s in row #(%s)' % (fields[index], rownumber))
                    rows.append(dict(zip(fields, row_empty_replaced)))
                    rownumber += 1
                f.close()

                del xlsx2csv

        return msg, fields, rows


    def run_tests(self):
        success = False
        msg = ['', 'Running tests']
        succes, msg_test = self.test_ks_missing_in_report()
        msg.extend(msg_test)

        return msg

    # Test to see if there are regels containing ks that are not
    # in a report (and therefore would not show up).
    def test_ks_missing_in_report(self):
        msg = ['Testing for ks in db that are not in ksgroups']
        success = True

        for ksgroup_name in model.ksgroup.available():
            ksgroup = model.ksgroup.load(ksgroup_name)
            ks_all = ksgroup.get_ks_recursive()
            for ks in model.regels.kostensoorten():
                if ks not in ks_all:
                    success = False
                    msg.append('WARNING kostensoort %s appears in DB but is not included in report %s' % (ks, ksgroup_name))

        if success:
            msg.append('test PASS')
        else:
            msg.append('test FAILED')

        return success, msg


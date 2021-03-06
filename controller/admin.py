from xlsx2csv import Xlsx2csv
import csv
import os
import tempfile
import shutil

from controller import Controller
import web
from web import form
import model.regels
import model.ksgroup
import model.orders
import model.users

from config import config
from model.functions import count_tables_other, remove_table


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
        self.form_drop_regels_table = form.Form(
            form.Dropdown('table', drop_down_options['empty_tables'],
                          form.notnull, description='Table to delete: '),
            form.Button('submit', value='dropTable')
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
            form.File('upload6'),
            form.Dropdown('type6', drop_down_options['empty_tables']),
            form.File('upload7'),
            form.Dropdown('type7', drop_down_options['empty_tables']),
            form.File('upload8'),
            form.Dropdown('type8', drop_down_options['empty_tables']),
            form.File('upload9'),
            form.Dropdown('type9', drop_down_options['empty_tables']),
            form.File('upload10'),
            form.Dropdown('type10', drop_down_options['empty_tables']),
            form.Button('submit', value='uploadRegels')
        )
        self.form_update_sap = form.Form(
            form.Textbox('sapdate', form.notnull, value=self.SAPupdate,
                         description='Date last SAP regels are uploaded'),
            form.Dropdown('sapperiode', drop_down_options['months'], value=self.lastperiode,
                          description='Last periode obligo/salarissen updated'),
            form.Button('submit', value='updateSapDates')
        )
        self.form_remove_graphs = form.Form(
            form.Dropdown('year', drop_down_options['empty_years_all'], form.notnull),
            form.Button('submit', value='removeGraphs')
        )

    def authorized(self):
        return model.users.check_permission(['admin'])

    def process_sub(self):
        # Handle posted forms
        if self.callType == 'POST':
            (valid_form, msg) = self.parse_forms()
            if valid_form:
                self.title = 'Admin Panel Results'
                self.body = self.render_simple(msg, redirect='admin')
                return  # prevent Get page from rendering

        # Display admin page on GET or invalid form post
        msg = ['Welcome to the Admin panel']
        msg.extend(self.run_tests())

        rendered = {}
        users, permissions = self.user_status()
        rendered['userAccess'] = self.webrender.user_access(users, permissions)
        status_regels, status_other_tables = self.db_status()
        rendered['dbStatus'] = self.webrender.db_status(status_regels, status_other_tables)

        rendered['forms'] = []
        rendered['forms'].append(self.webrender.form('Remove Regels From DB', self.form_remove_regels))
        rendered['forms'].append(self.webrender.form('Delete Regels Table', self.form_drop_regels_table))
        rendered['forms'].append(self.webrender.form('Upload File', self.form_upload))
        rendered['forms'].append(self.webrender.form('Update last SAP-update-date', self.form_update_sap))
        rendered['forms'].append(self.webrender.form('Remove graphs', self.form_remove_graphs))

        self.body = self.webrender.admin(msg, rendered)

    def user_status(self):
        users = []
        user_db = model.users.get_users()
        for user in user_db:
            perms = ', '.join(user.perms)
            users.append({'id': user.user_id, 'name': user.user_login, 'status': user.user_status,
                          'last login': user.user_last_login, 'perms': perms})

        permissions = []
        permissions_db = model.users.get_permissions()
        for permission in permissions_db:
            permissions.append({'id': permission.permission_id, 'name': permission.permission_codename,
                                'descr': permission.permission_desc})

        return users, permissions

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

        if form_used == 'dropTable' and self.form_drop_regels_table.validates():
            table = self.form_drop_regels_table['table'].value
            msg.append('Removing table %s from DB' % table)
            if remove_table(table):
                msg.append('Succes')
            else:
                msg.append('Failed!')

            valid_form = True

        if form_used == 'uploadRegels' and self.form_upload.validates():
            msg.extend(self.parse_upload_form())
            valid_form = True

        if form_used == 'updateSapDates' and self.form_update_sap.validates():
            msg.append('Updating last sap update date')
            model.regels.last_update(self.form_update_sap['sapdate'].value)
            model.regels.last_periode(self.form_update_sap['sapperiode'].value)
            valid_form = True

        if form_used == 'removeGraphs' and self.form_remove_graphs.validates():
            msg.extend(self.parse_remove_graphs())
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

    def parse_remove_graphs(self):
        jaar = self.form_remove_graphs['year'].value

        msg = ['Removing all graphs of year']

        if jaar == '*':
            msg.append("removing all")
            for year in model.regels.years():
                msg.append("removing graphs/%s/" % year)
                shutil.rmtree('graphs/%s/' % year, ignore_errors=True)
        else:
            msg.append("removing graphs/%s/" % jaar)
            shutil.rmtree('graphs/%s/' % jaar, ignore_errors=True)

        msg.append("Done!")
        return msg

    def parse_upload_form(self):
        msg = ['Start parsing of upload form']
        file_handles = web.input(upload1={}, upload2={}, upload3={}, upload4={}, upload5={}, upload6={}, upload7={}, upload8={}, upload9={}, upload10={})
        for i in range(1, 11):
            try:
                file_handle = eval("file_handles.upload%s" % i)
            except Exception:
                file_handle = None
            table = eval("self.form_upload['type%s'].value" % i)

            if file_handle is not None and table in config['mysql']['tables_regels'].keys():
                msg_read_xlsx, fields, rows = self.read_xlsx(file_handle, table)
                msg.extend(msg_read_xlsx)
                if fields is not None and rows is not None:
                    model.regels.add(table, fields, rows)

            if file_handle is not None and table == 'orderlijst':
                msg_read_xlsx, fields, rows = self.read_xlsx(file_handle, table)
                msg.extend(msg_read_xlsx)
                if fields is not None and rows is not None:
                    msg.extend(['Clearing previous orderlist from DB'])
                    model.orders.clear()  # every upload should be the whole list
                    msg.extend(['Adding new orderlist to DB'])
                    model.orders.add(fields, rows)
        return msg

    # Uploads and reads xlsx file
    # Returns fields and rows of the excel
    def read_xlsx(self, file_handle, table):
        msg = ['Starting uploading file']
        rows = []
        fields = []

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
                header_map = {y: x for x, y in config["SAPkeys"][table].iteritems()}

                for header in headers:
                    if header in header_map:
                        fields.append(header_map[header])
                    else:
                        msg.append('Unknown field in excel: ' + header)
                        msg.append('Import stopped!')
                        return msg, None, None

                for attribute, SAPkey in config["SAPkeys"][table].iteritems():
                    if attribute not in fields:
                        msg.append('Required field not in excel: ' + attribute)
                        return msg, None, None

                # Fill table from CSV
                msg.append('Parsing CSV')
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
        success, msg_test = self.test_ks_missing_in_report()
        msg.extend(msg_test)
        success, msg_test = self.test_old_orders()
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
                    msg.append(
                        'WARNING kostensoort %s appears in DB but is not included in report %s' % (ks, ksgroup_name))

        if success:
            msg.append('test PASS')
        else:
            msg.append('test FAILED')

        return success, msg

    # Test to see if there are ordernummers in the ordergroups/regels
    # that are no longer in the orderlist.
    def test_old_orders(self):
        msg = ['Testing for orders not in orderlist anymore']
        success = True

        if True:
            orders_active = model.orders.load().ordernummers()
            for og_file in model.ordergroup.available():
                ordergroup = model.ordergroup.load(og_file)
                orders_og_file = ordergroup.list_orders_recursive().keys()
                missing = list(set(orders_og_file)- set(orders_active))
                for order_missing in missing:
                    success = False
                    msg.append(
                        'WARNING order <a href="view?order=%s">%s</a> appears in %s but not in active orders' % (order_missing, order_missing, og_file))

        if success:
            msg.append('test PASS')
        else:
            msg.append('test FAILED')

        return success, msg

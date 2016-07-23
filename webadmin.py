"""
TODO
"""
import web
from config import config
import model
import os
from xlsx2csv import Xlsx2csv
import csv
import datetime


def checkDB():
    msg = ["Checking tables..."]
    tables = ['config', 'geboekt', 'obligo', 'plan', 'salaris']
    for table in tables:
        if model.check_table_exists(table):
            msg.append(table + " " + "ok")
        else:
            msg.append(table + " " + "FAIL")

    return msg


def updateGraphs(orderGroep):
    if orderGroep not in model.loadOrderGroepen():
        msg = ['Error ordergroep not found: ' + orderGroep]
        return msg
    else:
        msg = ['Ordergroep found!']
        msg = ['rebuilding Graphs (will take a while to appear)']
        os.system("python graph.py " + orderGroep)
    return msg


def parse_upload_form(render, form):
    x = web.input(myfile={})
    allowed = ['.xlsx']
    msg = ["Start upload"]

    table = web.input()['Type']
    table_allowed = False
    if table in ['geboekt', 'obligo', 'plan', 'salaris', 'salaris_begroting']:
        table_allowed = True

    if not table_allowed:
        msg.append('Type not selected!')
        return msg

    msg.append('Uploading file.')
    succes_upload = False
    if 'myfile' in x:
        pwd, filenamefull = os.path.split(x.myfile.filename)
        filename, extension = os.path.splitext(filenamefull)
        if extension in allowed:
            fout = open(table+'.xlsx','wb')
            fout.write(x.myfile.file.read())
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
        table_backup = table + datetime.datetime.now().strftime("%Y%m%d%H%M")
        msg.append('Rename '+table+' to ' + table_backup)
        if not model.move_table(table, table_backup):
            msg.append('Renaming table failed!')
            return msg
        msg.append('Renaming table succes')

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

    msg.append('Creating new table using headers')
    model.create_table(table, fields)

    # Fill table from CSV
    msg.append('Inserting data into table')
    rows = []
    rownumber = 1
    for row in reader:
        row_empty_replaced = [element or '0' for element in row]
        if row_empty_replaced != row:
            empty_indexes = [i for i, item in enumerate(row) if item == '']
            print empty_indexes
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

    return msg


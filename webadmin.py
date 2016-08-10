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
import tests

# Runs selected test in model.test
def run_tests():
    msg = ['Running tests']
    msg.append('Testing for ks that are not included in kostensoortgroepen')
    msg.extend(tests.ks_missing_in_report())
    return msg


def render_db_status(render):
    regelCount, yearsFound, totalCount = count_regels_tables()
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

    regelsTotal = ['Total', totalCount['total']]
    for year in sorted(list(yearsFound)):
        regelsTotal.append(totalCount[year])

    return render.webadmin_db_status(regelsHeaders, regelsBody, regelsTotal)


def count_regels_tables():
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

    return (regelCount, yearsFound, totals)


def parse_purgeRegelsForm():
    msg = ["Purging year from regels..."]
    jaar = web.input()['Year']
    if web.input()['Year'] != '%':
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


def parse_updateGraphs():
    msg = ['Parsing rebuild graph']

    orderGroep = web.input()['Ordergroep']
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

    if orderGroep not in model.loadOrderGroepen():
        msg.append('Error ordergroep not found: %s' % orderGroep)
        return msg

    msg = ['Ordergroep found!']
    msg = ['rebuilding Graphs (will take a while to appear)']
    msg.append("running: $python graph.py %s %s" % (orderGroep, jaar))
#TODO SOMEDAY fire proccess in sep. thread, graph.py write a log (clean everytime it starts), and webadmin poll if there is such a log running (report using msg)
    os.system("python graph.py %s %s" % (orderGroep, jaar))
    return msg


def parse_upload_form():
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

def upload_and_process_file(fileHandleName, table, fileHandle, msg):
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


import web
import hashlib
from config import config
import glob
import os
import csv
from Regel import Regel, specific_rules
from RegelList import RegelList

""""

TODO
    * Reserves in mysql
    * Prognose in mysql
    * Mee/tegenvallers in mysql
    * Authorisation in mysql
"""
db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"], host=config["mysql"]["host"])

# Returns a dictionary of regellists of select tables (or all if emtpy)
# {'geboekt': RegelList, '..': Regellist}
def get_regellist_per_table(tableNames=[], jaar=[], periodes=[], orders=[], kostensoorten=[]):
#TODO dit stukje naar een aparte 'privagte' functie van model (is nu dubbele code in functies)
    if not tableNames:
        tableNames = config["mysql"]["tables"]["regels"].keys()
    else:
        for name in tableNames:
            assert name in config["mysql"]["tables"]["regels"], "unknown table in model.get_reggellist_per_table: " + name

    regelsPerTable = {}
    for tableName in tableNames:
        query = mysql_regels_query(jaar, periodes, orders, kostensoorten)
        try:
            dbSelect = db.select(config["mysql"]["tables"]["regels"][tableName], where=query, vars=locals())
        except IndexError:
            return None

        regels = []
        for dbRegel in dbSelect:
            regel = Regel()
            regel.import_from_db_select(dbRegel, tableName)
            modifiedRegels = specific_rules(regel)
            for regel in modifiedRegels:
                regels.append(regel)

            regelsPerTable[tableName] = RegelList(regels)

    return regelsPerTable


# Returns a mysql query for getting regels from the db
def mysql_regels_query(jaar=[], periodes=[], orders=[], kostensoorten=[]):
    query = '1'

    if orders:
        query += ' AND  `ordernummer` IN (' + ','.join(str(order) for order in orders) + ')'

    if kostensoorten:
        query += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    if jaar:
        query += ' AND `jaar` IN (' + ','.join(str(jr) for jr in jaar) + ')'

    if periodes:
        query += ' AND `periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    return query


# gives possible years available
def get_years_available(tableNames=[]):
    jaren = set()
    if not tableNames:
        tableNames = config["mysql"]["tables"]["regels"].keys()
    else:
        for name in tableNames:
            assert name in config["mysql"]["tables"]["regels"], "unknown table in model.get_reggellist_per_table: " + name

    for table in tableNames:
        try: 
            jarenTable = db.query("SELECT DISTINCT(`jaar`) FROM `%s`" % (table) )
        except:
            jarenTable = []

        for dbRow in jarenTable:
            jaren.add(dbRow.jaar)

    return jaren


def delete_regels(jaar, tableNames=[]):
    if not tableNames:
        tableNames = config["mysql"]["tables"]["regels"].keys()
    else:
        for name in tableNames:
            assert name in config["mysql"]["tables"]["regels"], "unknown table in model.get_reggellist_per_table: " + name

    deletedTotal = 0
    for table in tableNames:
        try: 
            deleted = db.delete(table, where="jaar=$jaar", vars=locals())
        except:
            deleted = 0
        deletedTotal += deleted
        
    return deletedTotal


# Gives a list of allowed budgets for that user.
def get_budgets(verifyHash, salt):
    authorisation = load_auth_list()
    for user, orders in authorisation.iteritems():
        userHash = hashlib.sha224(user+salt).hexdigest()
        if userHash == verifyHash:
            ordersList = []
            for order in orders:
                if order[0] == '!':
                    order = order[1:]
                    if '%'in order:
                        for remove in get_orders(sqlLike=order):
                            ordersList.remove(long(remove))
                    else:
                        ordersList.remove(long(order))
                else:
                    if '%'in order:
                        ordersList.extend(get_orders(sqlLike=order))
                    else:
                        ordersList.append(order)
            return ordersList

    return []


def load_auth_list():
    authorisation = {}

    with open('data/authorisation/authorisations.txt') as f:
        for line in f.readlines():
            line = line.strip()
            if not line == '':
                authline = line.split()
                authorisation[authline[0]] = authline[1:]

    return authorisation


# Prints all the users and their hash so that
# you can access the correct pages using the hashes.
def gen_auth_list(salt):
    authorisations = load_auth_list()
    for user, orders in authorisations.iteritems():
        userHash = hashlib.sha224(user+salt).hexdigest()
        print user + ' - ' + userHash
        print 'has access to:'
        print orders
        print ''


# Read/write last sap-update date:
def last_update(newdate=''):
    if not check_table_exists('config'):
        sql = "CREATE TABLE `config` ( `key` varchar(255), `value` varchar(255) );"
        results = db.query(sql)
        sql = "INSERT INTO `config` ( `key`, `value`) VALUES ( 'sapdate', 'no date set' );"
        results = db.query(sql)

    if newdate == '':
        sqlwhere = "`key` = 'sapdate'"
        results = db.select('config', where=sqlwhere)
        sapdate = results[0]['value']
    else:
        db.update('config', where="`key` = 'sapdate'", value = newdate)
        sapdate = newdate

    return sapdate


# returns the list of all reserves
# TODO into mysql and use currentYear!
def get_reserves():
    from decimal import Decimal
    reserves = {}
    with open('data/reserves/2015.txt') as f:
        for line in f.readlines():
            line = line.strip()
            if not line == '':
                order, reserve = line.split()
                reserves[order] = -1*Decimal(reserve)

    return reserves


# Returns a sorted list of all orders
# in both geboekt and obligo
#TODO GET THIS FROM A CONFIG with names!
# TODO UPDATE config tables not manually geboekt/obligo
def get_orders(sqlLike='%'):

    geboekt = db.query("SELECT DISTINCT(`ordernummer`) FROM `geboekt` WHERE `ordernummer` LIKE '"+sqlLike+"'")
    obligo = db.query("SELECT DISTINCT(`ordernummer`) FROM `obligo` WHERE `ordernummer` LIKE '"+sqlLike+"'")

    orders = set()
    for regel in geboekt:
        orders.add(regel.ordernummer)

    for regel in obligo:
        orders.add(regel.ordernummer)

    orders = list(orders)
    orders.sort()

    return orders


# Returns a tuple of all kostensoorten and their names in order:
def get_kosten_soorten(order=0):
    if order == 0:
        geboektdb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `geboekt`")
        obligodb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `obligo`")
        plandb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `plan`")
    else:
        geboektdb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `geboekt` WHERE `ordernummer`=" + str(order))
        obligodb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `obligo` WHERE `ordernummer`=" + str(order))
        plandb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `plan` WHERE `ordernummer`=" + str(order))

    geboektks = {}
    for regel in geboektdb:
        geboektks[regel['kostensoort']] = regel['kostensoortnaam']

    obligoks = {}
    for regel in obligodb:
        obligoks[regel['kostensoort']] = regel['kostensoortnaam']

    planks = {}
    for regel in plandb:
        planks[regel['kostensoort']] = regel['kostensoortnaam']

    return geboektks, obligoks, planks

# Returns a list of ordergroepen available
# {name: path}
def loadOrderGroepen():
    OrderGroepen = {}
    for path in glob.glob("data\ordergroep\*"):
        OrderGroepen[os.path.split(path)[1]] = path

    return OrderGroepen


# Returns a dictionary of kostensoort groepen available
# {name: path}
def loadKSgroepen():
    KSgroepen = {}
    for path in glob.glob("data\kostensoortgroep\*"):
        KSgroepen[os.path.split(path)[1]] = path

    return KSgroepen


#TODO convert to mysql data not csv import.
#loads the CSV prognose sheet into regels
# returns a dictionary of regels, sorted by order#
def get_prognose_regels(jaar='', order=''):
    f = open('data/prognose/prognose.csv', 'rb')
    reader = csv.reader(f)
    prognose = {}
    for row in reader:
        if row[0].isdigit():
            regel = Regel()
            regel.tiepe = "Prognose"
            regel.order = row[0]
            regel.kosten = row[3]
            regel.jaar = row[1]
            regel.periode = row[2]
            regel.omschrijving = row[4]
            if regel.order in prognose:
                prognose[regel.order].append(regel)
            else:
                prognose[regel.order] = [regel]

    f.close()
    return prognose


# Checks if all tables exist: def check_table_exists(table):
def check_table_exists(table):
    results = db.query("SHOW TABLES LIKE '"+table+"'")
    if len(results) == 0:
        return False
    return True

# Moves a table in the db to a new one (renames!)
def move_table(table, target):
    if not check_table_exists(table):
        return False

    results = db.query("RENAME TABLE `sap`.`"+table+"` TO `sap`.`"+target+"`;")
    return True


# copyes a table in the db to target
def copy_table(table, target):
    if not check_table_exists(table):
        return False

    results = db.query("CREATE TABLE `sap`.`"+target+"` LIKE `sap`.`"+table+"`;")
    results = db.query("INSERT `sap`.`"+target+"` SELECT * FROM  `sap`.`"+table+"`;")
    return True


### SQL INJECTION POSSIBLE.. STRIP/VALUES FOR VALUES!
def create_table(table, fields):
    fieldsAndType = []
    for field in fields:
        sqlType = config["SAPkeys"]["types"][field]
        fieldsAndType.append('`'+field + '` ' + sqlType)

    sql = "CREATE TABLE " + table + " (" + ', '.join(fieldsAndType) + ");"
    results = db.query(sql)


# inserts multiple rows into the db. 
# Splits up the rows in bunches of 10k to prevent
# timeout of the mysqldb
def insert_into_table(table, rows):
# used for debugging when a row makes the mysql db crash
    rowChunks = chunk_rows(rows, 10000)
    for rows in rowChunks:
        db.multiple_insert(table, values=rows)


# Cuts op the row list in multiple rows
def chunk_rows(rows, chunkSize):
    for i in xrange(0, len(rows), chunkSize):
        yield rows[i:i+chunkSize]

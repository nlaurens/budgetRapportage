import web
import hashlib
from config import config
import glob
import csv
from Regel import Regel

""""

TODO
    * SAP-HR obligo omzetten naar meerdere regels (is er uit gehaald tijdelijk).
      Doe dit niet in model maar op de plek die hier last van heeft! Want het is elke keer anders
      b.v. voor salaris vervangen we hem door salaris regel! Snippet hier beneden:

            #DIRTY HACK for UL.nl SAP inrichting (obligo personeel wordt elke maand aangepast maar altijd op periode 1 gezet)
            # Hier maken we van die regel aparte regels voor elke resterende maand
            #for regel in regels:
            #    if regel.kostensoort == 411101:
            #        digits = [int(s) for s in regel.omschrijving.split() if s.isdigit()]
            #        periodeleft = range(digits[-2],digits[-1]+1)
            #        bedrag = regel.kosten/len(periodeleft)
            #        omschrijving = regel.omschrijving.decode('ascii', 'replace').encode('utf-8')
            #        for periode in periodeleft:
            #            regelNew = regel.copy()
            #            regelNew.omschrijving = omschrijving + '-per. ' + str(periode)
            #            regelNew.omschrijving
            #            regelNew.periode = periode
            #            regelNew.kosten = bedrag
            #            if regelNew.kostensoort in obligos:
            #                obligos[regelNew.kostensoort].append(regelNew)
            #            else:
            #                obligos[regelNew.kostensoort] = [regelNew]
            #    else:
            #        if regel.kostensoort in obligos:
            #            obligos[regel.kostensoort].append(regel)
            #        else:
            #            obligos[regel.kostensoort] = [regel]

    * Reserves in mysql
    * Prognose in mysql
    * Mee/tegenvallers in mysql
    * Authorisation in mysql
"""
db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"], host=config["mysql"]["host"])

# Returns a list of regels loaded from the dbSelect
# Function should by used by any get/load function that
# wants multiple regels from the mysql db.
def db_2_regels(dbSelect, tiepe):
    regels = []
    for dbRegel in dbSelect:
        regel = Regel()
        regel.import_from_db_select(dbRegel, tiepe)
        regels.append(regel)

    return regels

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

# Returns a list of boekingsRegel from the obligo table
def get_obligos_regels(jaar, periodes=[], orders=[], kostensoorten=[]):
    sqlwhere = '1'
    if orders:
        sqlwhere = '`ordernummer` IN (' + ','.join(str(order) for order in orders) + ')'

    if kostensoorten:
        if sqlwhere == '1':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    if sqlwhere == '1':
        sqlwhere = ' AND `jaar` = $jaar'
    else:
        sqlwhere += ' AND `jaar` = $jaar'

    if periodes:
        sqlwhere += ' AND `Periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        obligodb = db.select('obligo', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(obligodb, 'obligo')
    return  regels

# Returns a list of planregels from the geboekt table
def get_plan(jaar, order=0, kostensoorten=[]):
    if order > 0:
        sqlwhere = '`order`=$order'

    if kostensoorten:
        if sqlwhere == '':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    sqlwhere += ' AND `jaar` = $jaar'

    try:
        plandb = db.select('plan', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(plandb, 'plan')
    return  regels


# Returns a list of boekingsRegel from the geboekt table
def get_geboekt(jaar, periodes=[], order=0, kostensoorten=[]):

    if order > 0:
        sqlwhere = '`ordernummer`=$order'

    if kostensoorten:
        if sqlwhere == '':
            sqlwhere = '`kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    sqlwhere += ' AND `jaar` = $jaar'
    if periodes:
        sqlwhere += ' AND `periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        geboektdb = db.select('geboekt', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(geboektdb, 'geboekt')
    return  regels


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

# Returns a list of order available
def loadOrdergroepen():
    OG = glob.glob("data/grootboekgroep/*")

    return OG


# Returns a list of kostensoort groepen available
def loadKSgroepen():
    KSgroepen = glob.glob("data/kostensoortgroep/*")

    return KSgroepen


# TODO remove once everything is up and running
# Returns all the plan cost for an order:
def get_plan_totaal(jaar, order):
    sys.exit('model.get_plan_totaal is deprecated. Use model.get_plan() instead')


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


# Returns a list of geboekte salaris regels 
def get_salaris_geboekt_regels(jaar, periodes=[], orders=[], kostensoorten=[]):
    sqlwhere = '1'
    if orders:
        sqlwhere = '`order` IN (' + ','.join(str(order) for order in orders) + ')'

    if kostensoorten:
        if sqlwhere == '1':
            sqlwhere = '`kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

#TODO jaar en periode zitten niet in de db. Wel de datum. Slimme query schrijven die dit oppakt.
    #if sqlwhere == '1':
    #    sqlwhere = ' AND `'+config["SAPkeys"]["salaris"]["order"]+'Boekjaar` = $jaar'
    #else:
    #    sqlwhere += ' AND `'+config["SAPkeys"]["salaris"]["order"]+'Boekjaar` = $jaar'

    #if periodes:
    #    sqlwhere += ' AND `'+config["SAPkeys"]["salaris"]["order"]+'Periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        salarisdb = db.select('salaris', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(salarisdb, 'salaris')

    return regels


# Returns a list of begroting salaris regels 
def get_salaris_begroot_regels(jaar, orders=[]):
    sqlwhere = '1'
    if orders:
        sqlwhere = '`ordernummer` IN (' + ','.join(str(order) for order in orders) + ')'

    try:
        salarisdb = db.select('salaris_begroting', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(salarisdb, 'salaris_begroting')

    return regels


# Checks if all tables exist: def check_table_exists(table):
def check_table_exists(table):
    results = db.query("SHOW TABLES LIKE '"+table+"'")
    if len(results) == 0:
        return False
    return True


def move_table(table, target):
    if not check_table_exists(table):
        return False

    results = db.query("RENAME TABLE `sap`.`"+table+"` TO `sap`.`"+target+"`;")
    return True


### SQL INJECTION POSSIBLE.. STRIP/VALUES FOR VALUES!
def create_table(table, fields):
    fieldsAndType = []
    for field in fields:
        sqlType = config["SAPkeys"]["types"][field]
        fieldsAndType.append('`'+field + '` ' + sqlType)

    sql = "CREATE TABLE " + table + " (" + ', '.join(fieldsAndType) + ");"
    results = db.query(sql)


def insert_into_table(table, rows):
    db.multiple_insert(table, values=rows)

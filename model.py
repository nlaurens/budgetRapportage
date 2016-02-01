import web
import hashlib
from config import config
import glob
import csv
from Regel import Regel

#TODO vervang alle SQL query door de config params ipv de hardcoded kolom namen.
#TODO vervang alle *_db_2_regel door 1 functie. Met de nieuwe config zou alles te mappen
#     moeten zijn door 1 functie. Wel zo dat er misschien wat 'if type=salaris: parse datum' etc. erin.
#     Deze functie geeft een LIJST geen dictionary. Daarna kan je functie aanroepen
#     die deze lijst in een dict sorteert afhankelijk van welke key je wilt
#     obligos = get_obligos()
#     obligos_per_ks = list_2_dict('ks') <-- veel duidelijk

""""

TODO
    * SAP-HR obligo omzetten naar meerdere regels (is er uit gehaald tijdelijk).
      Doe dit niet in model maar op de plek die hier last van heeft! Want het is elke keer anders
      b.v. voor salaris vervangen we hem door salaris regel!

"""
db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"], host=config["mysql"]["host"])

###########################################################
# OLD functions, should be removed later by using the 2db functions

# Returns a list of boekingsRegel from the obligo table
def get_obligos(jaar, periodes=[], order=0, kostensoorten=[]):
    sqlwhere = '1'
    if order > 0:
        sqlwhere = '`order`=$order'

    if kostensoorten:
        if sqlwhere == '1':
            sqlwhere = '`kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    if sqlwhere == '1':
        sqlwhere = ' AND `jaar` = $jaar'
    else:
        sqlwhere += ' AND `jaar` = $jaar'

    if periodes:
        sqlwhere += ' AND `periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        obligodb = db.select('obligo', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    return obligo_db_2_regels(obligodb)

# Returns a dict containing a list of regels at key kostensoort
# ie. obligos['kostensoort'] = [ <regel>, <regel>, .. ]
def obligo_db_2_regels(obligodb):

    obligos = {}
    for regelDB in obligodb:
        regel = Regel()

        regel.tiepe = 'Obligo'
        regel.order = regelDB['order']
        regel.kostensoort = regelDB['kostensoort']
        regel.naamkostensoort = regelDB['kostensoortnaam']
        regel.kosten = regelDB['kosten']
        regel.jaar = regelDB['jaar']
        regel.periode = regelDB['periode']
        regel.omschrijving = regelDB['omschrijving']
        regel.documentnummer = regelDB['documentnummer']

#DIRTY HACK for UL.nl SAP inrichting (obligo personeel wordt elke maand aangepast maar altijd op periode 1 gezet)
        if regel.kostensoort == 411101:
            digits = [int(s) for s in regel.omschrijving.split() if s.isdigit()]
            periodeleft = range(digits[-2],digits[-1]+1)
            bedrag = regel.kosten/len(periodeleft)
            omschrijving = regel.omschrijving.decode('ascii', 'replace').encode('utf-8')
            for periode in periodeleft:
                regelNew = regel.copy()
                regelNew.omschrijving = omschrijving + '-per. ' + str(periode)
                regelNew.omschrijving
                regelNew.periode = periode
                regelNew.kosten = bedrag
                if regelNew.kostensoort in obligos:
                    obligos[regelNew.kostensoort].append(regelNew)
                else:
                    obligos[regelNew.kostensoort] = [regelNew]
        else:
            if regel.kostensoort in obligos:
                obligos[regel.kostensoort].append(regel)
            else:
                obligos[regel.kostensoort] = [regel]

    return obligos





###########################################################

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


# returns the list of all reserves
def get_reserves():
    reserves = {}
    with open('data/reserves/2015.txt') as f:
        for line in f.readlines():
            line = line.strip()
            if not line == '':
                order, reserve = line.split()
                reserves[order] = -1*float(reserve)

    return reserves


# Returns a sorted list of all orders
# in both geboekt and obligo
def get_orders(sqlLike='%'):

    geboekt = db.query("SELECT DISTINCT(`order`) FROM `geboekt` WHERE `order` LIKE '"+sqlLike+"'")
    obligo = db.query("SELECT DISTINCT(`order`) FROM `obligo` WHERE `order` LIKE '"+sqlLike+"'")

    orders = set()
    for regel in geboekt:
        orders.add(regel.Order)

    for regel in obligo:
        orders.add(regel.Order)

    orders = list(orders)
    orders.sort()

    return orders

# Returns a list of boekingsRegel from the obligo table
def get_obligos_regels(jaar, periodes=[], orders=[], kostensoorten=[]):
    sqlwhere = '1'
    if orders:
        sqlwhere = '`'+config["SAPkeys"]["obligo"]["order"]+'` IN (' + ','.join(str(order) for order in orders) + ')'

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


    return  regels

# Returns a dict containing a list of regels at key kostensoort
# ie. obligos['kostensoort'] = [ <regel>, <regel>, .. ]
def plan_db_2_regels(db):

    plans = {}
    for regelDB in db:
        regel = Regel()

        regel.tiepe = 'Plan'
        regel.periode = 0
        regel.order = regelDB[config["SAPkeys"]["plan"]["order"]]
        regel.kostensoort = regelDB[config["SAPkeys"]["plan"]["ks"]]
        regel.naamkostensoort = regelDB[config["SAPkeys"]["plan"]["ks-naam"]]
        regel.kosten = float(regelDB[config["SAPkeys"]["plan"]["kosten"]].replace(',',''))
        regel.jaar = regelDB[config["SAPkeys"]["plan"]["jaar"]]
        regel.documentnummer = regelDB[config["SAPkeys"]["plan"]["doc.nr."]]

        if regel.kostensoort in plans:
            plans[regel.kostensoort].append(regel)
        else:
            plans[regel.kostensoort] = [regel]

    return plans


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

    return plan_db_2_regels(plandb)


# Returns a list of boekingsRegel from the geboekt table
def get_geboekt(jaar, periodes=[], order=0, kostensoorten=[]):

    if order > 0:
        sqlwhere = '`order`=$order'

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

    return geboekt_db_2_regel(geboektdb)


# Returns a dictionary that contains a list of regels per key kostensoort
# ie. geboekt['kostensoort'] = [regels]
def geboekt_db_2_regel(geboektdb):

    geboekt = {}
    for regelDB in geboektdb:
        regel = Regel()
        regel.tiepe = "Geboekt"
        regel.order = regelDB['order']
        regel.kostensoort = regelDB['kostensoort']
        regel.naamkostensoort = regelDB['kostensoortnaam']
        regel.kosten = regelDB['kosten']
        regel.jaar = regelDB['jaar']
        regel.periode = regelDB['periode']
        regel.omschrijving = regelDB['omschrijving']
        regel.documentnummer = regelDB['documentnummer']
        if regel.kostensoort in geboekt:
            geboekt[regel.kostensoort].append(regel)
        else:
            geboekt[regel.kostensoort] = [regel]

    return geboekt


# Returns a tuple of all kostensoorten and their names in order:
def get_kosten_soorten(order=0):
    if order == 0:
        geboektdb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `geboekt`")
        obligodb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `obligo`")
        plandb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `plan`")
    else:
        geboektdb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `geboekt` WHERE `order`=" + str(order))
        obligodb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `obligo` WHERE `order`=" + str(order))
        plandb = db.query("SELECT DISTINCT(`kostensoort`), `kostensoortnaam` FROM `plan` WHERE `order`=" + str(order))

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


# Returns all the plan cost for an order:
def get_plan_totaal(jaar, order):
    plan = 0
    sqlwhere = '`order`=$order AND `jaar`=$jaar'
    plandb = db.select('plan', where=sqlwhere, vars=locals())
    for regelDB in plandb:
        plan += float(regelDB[config["SAPkeys"]["plan"]["kosten"]].replace(',',''))

    return -1*plan

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
        sqlwhere = '`'+config["SAPkeys"]["salaris_begroting"]["order"]+'` IN (' + ','.join(str(order) for order in orders) + ')'

    try:
        salarisdb = db.select('salaris_begroting', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    regels = db_2_regels(salarisdb, 'salaris_begroting')

    return regels


# Returns a list of regels loaded from the dbSelect
def db_2_regels(dbSelect, tiepe):
    regels = []
    for dbRegel in dbSelect:
        regel = Regel()
        regel.import_from_db_select(dbRegel, tiepe)
        regels.append(regel)

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

    for row in rows:
        sqlVars = {}
        sqlVars['VALUES'] = row
        result = db.query("INSERT INTO "+table+" VALUES $VALUES;", vars=sqlVars)

import web
import hashlib
from config import config
import glob

#TODO vervang alle SQL query door de config params ipv de hardcoded kolom namen.

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"], host=config["mysql"]["host"])

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

# returns the list of all begrote orders
def get_begroting():
    begroting = {}
    with open('data/begroting/2015.txt') as f:
        for line in f.readlines():
            line = line.strip()
            if not line == '':
                order, bedrag = line.split()
                begroting[order] = bedrag

    return begroting

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

    geboekt = db.query("SELECT DISTINCT(`Order`) FROM `geboekt` WHERE `Order` LIKE '"+sqlLike+"'")
    obligo = db.query("SELECT DISTINCT(`Order`) FROM `obligo` WHERE `Order` LIKE '"+sqlLike+"'")

    orders = set()
    for regel in geboekt:
        orders.add(regel.Order)

    for regel in obligo:
        orders.add(regel.Order)

    orders = list(orders)
    orders.sort()

    return orders

# Returns a list of boekingsRegel from the obligo table
def get_obligos(jaar, periodes=[], order=0, kostensoorten=[]):
    sqlwhere = '1'
    if order > 0:
        sqlwhere = '`Order`=$order'

    if kostensoorten:
        if sqlwhere == '1':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    if sqlwhere == '1':
        sqlwhere = ' AND `Boekjaar` = $jaar'
    else:
        sqlwhere += ' AND `Boekjaar` = $jaar'

    if periodes:
        sqlwhere += ' AND `Periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        obligodb = db.select('obligo', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    return obligo_db_2_regels(obligodb)

# Returns a dict containing a list of regels at key kostensoort
# ie. obligos['kostensoort'] = [ <regel>, <regel>, .. ]
def plan_db_2_regels(db):
    from BoekingsRegel import BoekingsRegel

    plans = {}
    for regelDB in db:
        regel = BoekingsRegel()

        regel.tiepe = 'Plan'
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

# Returns a dict containing a list of regels at key kostensoort
# ie. obligos['kostensoort'] = [ <regel>, <regel>, .. ]
def obligo_db_2_regels(obligodb):
    from BoekingsRegel import BoekingsRegel

    obligos = {}
    for regelDB in obligodb:
        regel = BoekingsRegel()

        regel.tiepe = 'Obligo'
        regel.order = regelDB[config["SAPkeys"]["obligo"]["order"]]
        regel.kostensoort = regelDB[config["SAPkeys"]["obligo"]["ks"]]
        regel.naamkostensoort = regelDB[config["SAPkeys"]["obligo"]["ks-naam"]]
        regel.kosten = float(regelDB[config["SAPkeys"]["obligo"]["kosten"]].replace(',',''))
        regel.jaar = regelDB[config["SAPkeys"]["obligo"]["jaar"]]
        regel.periode = regelDB[config["SAPkeys"]["obligo"]["periode"]]
        regel.omschrijving = regelDB[config["SAPkeys"]["obligo"]["descr"]]
        regel.documentnummer = regelDB[config["SAPkeys"]["obligo"]["doc.nr."]]

        if regel.kostensoort in obligos:
            obligos[regel.kostensoort].append(regel)
        else:
            obligos[regel.kostensoort] = [regel]

    return obligos

# Returns a list of planregels from the geboekt table
def get_plan(jaar, order=0, kostensoorten=[]):

    if order > 0:
        sqlwhere = '`Order`=$order'

    if kostensoorten:
        if sqlwhere == '':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    sqlwhere += ' AND `Boekjaar` = $jaar'

    try:
        plandb = db.select('plan', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    return plan_db_2_regels(plandb)


# Returns a list of boekingsRegel from the geboekt table
def get_geboekt(jaar, periodes=[], order=0, kostensoorten=[]):

    if order > 0:
        sqlwhere = '`Order`=$order'

    if kostensoorten:
        if sqlwhere == '':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    sqlwhere += ' AND `Jaar` = $jaar'
    if periodes:
        sqlwhere += ' AND `Periode` IN (' + ','.join(str(periode) for periode in periodes) + ')'

    try:
        geboektdb = db.select('geboekt', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    return geboekt_db_2_regel(geboektdb)


# Returns a dictionary that contains a list of regels per key kostensoort
# ie. geboekt['kostensoort'] = [regels]
def geboekt_db_2_regel(geboektdb):
    from BoekingsRegel import BoekingsRegel

    geboekt = {}
    for regelDB in geboektdb:
        regel = BoekingsRegel()
        regel.tiepe = "Geboekt"
        regel.order = regelDB[config["SAPkeys"]["geboekt"]["order"]]
        regel.kostensoort = regelDB[config["SAPkeys"]["geboekt"]["ks"]]
        regel.naamkostensoort = regelDB[config["SAPkeys"]["geboekt"]["ks-naam"]]
        regel.kosten = float(regelDB[config["SAPkeys"]["geboekt"]["kosten"]].replace(',',''))
        regel.jaar = regelDB[config["SAPkeys"]["geboekt"]["jaar"]]
        regel.periode = regelDB[config["SAPkeys"]["geboekt"]["periode"]]
        regel.omschrijving = regelDB[config["SAPkeys"]["geboekt"]["descr"]]
        regel.documentnummer = regelDB[config["SAPkeys"]["geboekt"]["doc.nr."]]
        if regel.kostensoort in geboekt:
            geboekt[regel.kostensoort].append(regel)
        else:
            geboekt[regel.kostensoort] = [regel]

    return geboekt


# Returns a tuple of all kostensoorten and their names in order:
def get_kosten_soorten(order=0):
    if order == 0:
        geboektdb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `geboekt`")
        obligodb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `obligo`")
        plandb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `plan`")
    else:
        geboektdb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `geboekt` WHERE `order`=" + str(order))
        obligodb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `obligo` WHERE `order`=" + str(order))
        plandb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `plan` WHERE `order`=" + str(order))

    geboektks = {}
    for regel in geboektdb:
        geboektks[regel['Kostensoort']] = regel['Naam v. kostensoort']

    obligoks = {}
    for regel in obligodb:
        obligoks[regel['Kostensoort']] = regel['Naam v. kostensoort']

    planks = {}
    for regel in plandb:
        planks[regel['Kostensoort']] = regel['Naam v. kostensoort']

    return geboektks, obligoks, planks


# Returns a list of kostensoort groepen available
def loadKSgroepen():
    KSgroepen = glob.glob("data/kostensoortgroep/*")

    return KSgroepen


# Returns all the plan cost for an order:
def get_plan_totaal(jaar, order):
    plan = 0
    sqlwhere = '`Order`=$order AND `Boekjaar`=$jaar'
    plandb = db.select('plan', where=sqlwhere, vars=locals())
    for regelDB in plandb:
        plan += float(regelDB[config["SAPkeys"]["plan"]["kosten"]].replace(',',''))

    return -1*plan

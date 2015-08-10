import web
import hashlib
from config import config
import glob

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"], host=config["mysql"]["host"])

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
                reserves[order] = reserve

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
def get_obligos(order=0, kostensoorten=[]):
    sqlwhere = '1'
    if order > 0:
        sqlwhere = '`Order`=$order'

    if kostensoorten:
        if sqlwhere == '1':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

    try:
        obligodb = db.select('obligo', where=sqlwhere, vars=locals())
    except IndexError:
        return None

    return obligo_db_2_regels(obligodb)


# Returns a dict containing a list of regels at key kostensoort
# ie. obligos['kostensoort'] = [ <regel>, <regel>, .. ]
def obligo_db_2_regels(obligodb):
    from BoekingsRegel import BoekingsRegel

    obligos = {}
    for regeldb in obligodb:
        regel = BoekingsRegel()
        regel.order = regeldb['Order']
        regel.kostensoort = regeldb['Kostensoort']
        regel.naamkostensoort = regeldb['Naam v. kostensoort']
        regel.kosten = regeldb['Waarde/CO-valuta']
        regel.documentnummer = 5#regelDB['Nr. referentiedoc.']
        regel.personeelsnummer = 'nvt'#regelDB['Personeelsnummer']
        regel.hoeveelheid = 'nvt'#regelDB['Hoeveelheid totaal']
        regel.jaar = regeldb['Boekjaar']
        regel.periode = regeldb['Periode']
        regel.omschrijving = regeldb['Omschrijving']
        regel.tiepe = 'Obligo'
        if regel.kostensoort in obligos:
            obligos[regel.kostensoort].append(regel)
        else:
            obligos[regel.kostensoort] = [regel]

    return obligos


# Returns a list of boekingsRegel from the geboekt table
def get_geboekt(order=0, kostensoorten=[]):

    sqlwhere = '1'
    if order > 0:
        sqlwhere = '`Order`=$order'

    if kostensoorten:
        if sqlwhere == '':
            sqlwhere = '`Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'
        else:
            sqlwhere += ' AND `Kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten) + ')'

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
        regel.order = regelDB['Order']
        regel.kostensoort = regelDB['Kostensoort']
        regel.naamkostensoort = regelDB['Naam v. kostensoort']
        regel.kosten = float(regelDB['Waarde/CO-valuta'].replace(',', '.'))
        regel.documentnummer = regelDB['Documentnummer']
        regel.personeelsnummer = regelDB['Personeelsnummer']
        regel.hoeveelheid ='nvt'# int(regelDB['Totl. ingev. hoevh.'])
        regel.jaar = regelDB['Boekjaar']
        regel.periode = regelDB['Periode']
        regel.omschrijving = regelDB['Omschrijving']
        regel.tiepe = 'Geboekt'
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
    else:
        geboektdb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `geboekt` WHERE `order`=" + str(order))
        obligodb = db.query("SELECT DISTINCT(`Kostensoort`), `Naam v. kostensoort` FROM `obligo` WHERE `order`=" + str(order))

    geboektks = {}
    for regel in geboektdb:
        geboektks[regel['Kostensoort']] = regel['Naam v. kostensoort']

    obligoks = {}
    for regel in obligodb:
        obligoks[regel['Kostensoort']] = regel['Naam v. kostensoort']

    return geboektks, obligoks


# Returns a list of kostensoort groepen available
def loadKSgroepen():
    KSgroepen = glob.glob("data/kostensoortgroep/*")

    return KSgroepen

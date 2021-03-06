import web
from config import config
from budget import Regel, RegelList
from functions import check_table_exists, add_items_to_db

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"],
                  host=config["mysql"]["host"])


def load(table_names_load, years_load=None, periods_load=None, orders_load=None, kostensoorten_load=None):
    """
    .load(years=[], periods=[], orders=[], tablesNames=[], kostensoorten=[])
        input: tablesNames as list of str,
        optional inputs:
            years as list of int,
            periods_load as list of int or as string ('ALL', 'Q1', 'Q2', 'Q3', 'Q4')
            orders as list of int,
            kostensoorten as list of int
        output: RegelList
    """
    for name in table_names_load:
        assert name in config["mysql"]["tables_regels"], "unknown table in model.get_reggellist_per_table: " + name


    periods = None
    if periods_load == [12]:
        periods = [12, 13, 14, 15, 16]
    elif periods_load == 'ALL':
        periods = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    elif periods_load == 'Q1':
        periods = [0, 1, 2, 3]
    elif periods_load == 'Q2':
        periods = [4, 5, 6]
    elif periods_load == 'Q3':
        periods = [7, 8, 9]
    elif periods_load == 'Q4':
        periods = [10, 11, 12, 13, 14, 15, 16]


    regels = []
    for table_name in table_names_load:
        query = '1'
        if orders_load:
            query += ' AND  `ordernummer` IN (' + ','.join(str(order) for order in orders_load) + ')'
        if kostensoorten_load:
            query += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten_load) + ')'
        if years_load:
            query += ' AND `jaar` IN (' + ','.join(str(jr) for jr in years_load) + ')'
        if periods:
            query += ' AND `periode` IN (' + ','.join(str(period) for period in periods) + ')'
        try:
            db_select = db.select(config["mysql"]["tables_regels"][table_name], where=query, vars=locals())
        except IndexError:
            return None

        for dbRegel in db_select:
            regel = Regel()
            regel.import_from_db_select(dbRegel, table_name)
            modified_regels = __specific_rules(regel)
            for regel in modified_regels:
                regels.append(regel)

    return RegelList(regels)


def __specific_rules(regel):
    # .__specific_rules(regel)
    #   modification of the regels in the db based on their content should be written
    #   here. Note this changes per setup.
    modified_regels = [regel]  # one regel can be replaced by multiple hence the list.

    # Specific rules per tiepe
    if regel.tiepe == 'plan':
        regel.periode = 1
        regel.omschrijving = 'begroting'

    if regel.tiepe == 'obligo':
        # Prognose afschrijvingen omzetten in 1 obligo
        if regel.kostensoort == 432100 or regel.kostensoort == 411101:
            modified_regels = []  # Remove old regel from list, we will ad new ones
            digits = [int(s) for s in regel.omschrijving.split() if s.isdigit()]
            assert 0 < len(digits) < 3
            if len(digits) == 2:
                periodeleft = range(digits[-2], digits[-1] + 1)
            else:  # omschrijving in dec is : 'periode 12' niet 'periode xx t/m yy'
                periodeleft = [12]
            bedrag = regel.kosten / len(periodeleft)
            omschrijving = regel.omschrijving.decode('ascii', 'replace').encode('utf-8')
            for periode in periodeleft:
                regel_new = regel.copy()
                regel_new.omschrijving = omschrijving + '-per. ' + str(periode)
                regel_new.periode = periode
                regel_new.kosten = bedrag
                modified_regels.append(regel_new)

                # if tiepe == 'obligo' or 'geboekt':
                # self.omschrijving = self.omschrijving.decode('ascii', 'replace').encode('utf-8')

    return modified_regels


def count():
    """
    .count()
        input: None
        output: dict.value: number of regels as int,
                dict.key: tableName as str
    """
    table_names = sorted(config["mysql"]["tables_regels"].values())
    years_in_db = years()

    count_regels = {}
    for table in table_names:
        count_regels[table] = {}
        for year in years_in_db:
            try:
                results = db.query("SELECT COUNT(*) AS total_regels FROM %s WHERE `jaar`=%s " % (table, year))
            except Exception:
                results = None

            if results:
                count_regels[table][year] = int(results[0].total_regels)
            else:
                count_regels[table][year] = 0

    return count_regels


def last_update(newdate=''):
    """
    .last_update(newdate='')
        input: newdate to be written in the db as str
        output: last sap update from db as a string
    """
    if not check_table_exists('config'):
        sql = "CREATE TABLE `config` ( `key` varchar(255), `value` varchar(255) );"
        results = db.query(sql)

        sql = "INSERT INTO `config` ( `key`, `value`) VALUES ( 'sapdate', 'no date set' );"
        results = db.query(sql)

        sql = "INSERT INTO `config` ( `key`, `value`) VALUES ( 'lastperiode', '0' );"
        results = db.query(sql)

    if newdate == '':
        sqlwhere = "`key` = 'sapdate'"
        results = db.select('config', where=sqlwhere)
        sapdate = results[0]['value']
    else:
        db.update('config', where="`key` = 'sapdate'", value=newdate)
        sapdate = newdate

    return sapdate


def last_periode(newperiode=''):
    """
    .last_periode(newperiode='')
        input: newperiode to be written in the db as str
        output: last periode salaris was booked from db as int
    """
    if not check_table_exists('config'):
        sql = "CREATE TABLE `config` ( `key` varchar(255), `value` varchar(255) );"
        results = db.query(sql)

        sql = "INSERT INTO `config` ( `key`, `value`) VALUES ( 'lastperiode', '0' );"
        results = db.query(sql)

        sql = "INSERT INTO `config` ( `key`, `value`) VALUES ( 'sapdate', 'no date set' );"
        results = db.query(sql)

    if newperiode == '':
        sqlwhere = "`key` = 'lastperiode'"
        results = db.select('config', where=sqlwhere)
        try:
            lastperiode = int(results[0]['value'])
        except:
            lastperiode = 0
    else:
        newperiode = int(newperiode)
        db.update('config', where="`key` = 'lastperiode'", value=newperiode)
        lastperiode = newperiode

    return lastperiode


def years():
    """
    .years()
        input: None
        output: years in db available as list of int
    """
    years_in_db = list(map(int, __select_distinct('jaar')))
    return sorted(years_in_db)


def orders():
    """
    .orders()
        input: None
        output: orders in db available as list of int
    """
    orders_in_db = list(map(int, __select_distinct('ordernummer')))
    return sorted(orders_in_db)


def kostensoorten():
    """
    .kostensoorten()
        input: None
        output: kostensoorten in db available as list of int
    """
    ks = list(map(int, __select_distinct('kostensoort')))
    return sorted(ks)


def __select_distinct(regel_attribute):
    # Returns a set of distinct values of the requested attribute
    # used by: years(), orders(), kostensoorten()
    distinct = set()
    table_names = config["mysql"]["tables_regels"].values()

    for table_name in table_names:
        try:
            table = db.query("SELECT DISTINCT(`%s`) FROM `%s`" % (regel_attribute, table_name))
        except Exception:
            table = None

        if table:
            for db_row in table:
                distinct.add(getattr(db_row, regel_attribute))

    return distinct


def delete(years_delete=None, table_names_delete=None):
    """
    .delete(years=[], tableNames=[])
        input: years al list of int, tableNames as list of str
        output: total amount of regels deleted as int
    """
    if not table_names_delete:
        table_names_delete = config["mysql"]["tables_regels"].keys()
    else:
        for name in table_names_delete:
            assert name in config["mysql"]["tables_regels"], "unknown table in model.get_reggellist_per_table: " + name

    if years_delete:
        sql_where = '`jaar` IN (' + ','.join(str(jr) for jr in years_delete) + ')'
    else:
        sql_where = '1'

    deleted_total = 0
    for table in table_names_delete:

        try:
            deleted = db.delete(config["mysql"]["tables_regels"][table], where=sql_where)
        except Exception:
            deleted = 0
        deleted_total += deleted

    return deleted_total


def add(table, fields, rows):
    """
    .add(table, fields, rows)
        input: table as str, fields as list of str, rows as list of str
        output: msg-queue as list of str
    """
    add_items_to_db(config['mysql']['tables_regels'][table], fields, rows)

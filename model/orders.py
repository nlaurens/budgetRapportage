import web
from config import config
from budget import Order, OrderList
from functions import add_items_to_db

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"],
                  host=config["mysql"]["host"])

def activiteitencodes():
    """
        .activiteitencodes
        input: None
        output: List of unique activiteitencodes as str
    """
    actcodes = list(map(str, __select_distinct('activiteitencode')))
    return sorted(actcodes)


def __select_distinct(regel_attribute):
    # Returns a set of distinct values of the requested attribute
    # used by: years(), orders(), kostensoorten()
    distinct = set()
    table_name = config["mysql"]["tables_other"]["orderlijst"]

    try:
        table = db.query("SELECT DISTINCT(`%s`) FROM `%s`" % (regel_attribute, table_name))
    except Exception:
        table = None

    if table:
        for db_row in table:
            distinct.add(getattr(db_row, regel_attribute))

    return distinct


def load(BH=None):
    """
        .Load
        input: none
        output: OrderList instance
    """
    #TODO
    #query = '1'
    #if orders_load:
    #    query += ' AND  `ordernummer` IN (' + ','.join(str(order) for order in orders_load) + ')'
    #if kostensoorten_load:
    #    query += ' AND `kostensoort` IN (' + ','.join(str(ks) for ks in kostensoorten_load) + ')'
    #if years_load:
    #    query += ' AND `jaar` IN (' + ','.join(str(jr) for jr in years_load) + ')'
    #if periods:
    #    query += ' AND `periode` IN (' + ','.join(str(period) for period in periods) + ')'

    try:
        db_select = db.select(config["mysql"]["tables_other"]["orderlijst"], where=query, vars=locals())
    except IndexError:
        return None

    orders = []
    for dbOrder in db_select:
        order = Order()
        order.import_from_db_select(dbOrder)
        modified_orders = __specific_rules(order)
        for order in modified_orders:
            orders.append(order)

    return OrderList(orders)


def __specific_rules(order):
    #  .__specific_rules(order)
    #  modification of order can be done here
    #  note this changes per setup
    modified_orders = [order]

    return modified_orders


def add(fields, rows):
    """
    .add(table, fields, rows)
        input: table as str, fields as list of str, rows as list of str
        output: msg-queue as list of str
    """
    add_items_to_db(config["mysql"]["tables_other"]["orderlijst"], fields, rows)


def clear():
    """
    .clear()
        input: none
        output: total amount of regels deleted as int
    """
    sql_where = '1'
    try:
        deleted = db.delete(config["mysql"]["tables_other"]["orderlijst"], where=sql_where)
    except Exception:
        deleted = 0

    return deleted

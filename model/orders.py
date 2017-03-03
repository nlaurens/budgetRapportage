import web
from config import config
from budget import Order, OrderList
from functions import add_items_to_db

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"],
                  host=config["mysql"]["host"])

"""
    .activiteitencodes
    input: None
    output: List of unique activiteitencodes as str
"""


def activiteitencodes():
    actcodes = list(map(str, __select_distinct('activiteitencode')))
    return sorted(actcodes)


# Returns a set of distinct values of the requested attribute
# used by: years(), orders(), kostensoorten()
def __select_distinct(regel_attribute):
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


"""
    .Load
    input: none
    output: OrderList instance
"""


def load():
    try:
        db_select = db.select(config["mysql"]["tables_other"]["orderlijst"])
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


#  .__specific_rules(order)
#  modification of order can be done here
#  note this changes per setup
def __specific_rules(order):
    modified_orders = [order]

    return modified_orders


"""
.add(table, fields, rows)
    input: table as str, fields as list of str, rows as list of str
    output: msg-queue as list of str
"""


def add(fields, rows):
    add_items_to_db(config["mysql"]["tables_other"]["orderlijst"], fields, rows)


"""
.clear()
    input: none
    output: total amount of regels deleted as int
"""


def clear():
    sql_where = '1'
    try:
        deleted = db.delete(config["mysql"]["tables_other"]["orderlijst"], where=sql_where)
    except Exception:
        deleted = 0

    return deleted

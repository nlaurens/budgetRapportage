import web
from config import config
from budget import Order, OrderList
from functions import add_items_to_db

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"],
                  host=config["mysql"]["host"])


"""
    input: none
    output: list of dict items
"""
def load():
    try:
        db_select = db.select(config["mysql"]["tables"]["orderlijst"])
    except IndexError:
            return None

    orders = []
    for dbOrder in db_select:
        order = Order()
        order.import_from_db_select(dbOrder)
        orders.append(order)

    return OrderList(orders)


"""
.add(table, fields, rows)
    input: table as str, fields as list of str, rows as list of str
    output: msg-queue as list of str
"""
def add(fields, rows):
    add_items_to_db(config["mysql"]["tables"]["orderlijst"], fields, rows)


"""
.clear()
    input: none
    output: total amount of regels deleted as int
"""
def clear():
    sql_where = '1'
    try:
        deleted = db.delete(config["mysql"]["tables"]["orderlijst"], where=sql_where)
    except Exception:
        deleted = 0

    return deleted

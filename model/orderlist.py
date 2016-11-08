import web
from config import config

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

    #TODO replace with loading like for regels (model.budget.orderlist <- aanmaken)
    orderlist = []
    for dbRegel in db_select:
        orderlist_item = {}
        orderlist_item['order'] = dbRegel['ordernummer']
        orderlist_item['omschrijving'] = dbRegel['ordernaam']
        orderlist_item['budgethouder'] = dbRegel['budgethouder']
        orderlist_item['activiteitenhouder'] = dbRegel['activiteitenhouder']
        orderlist_item['sub.act.code'] = dbRegel['subactiviteitencode']
        orderlist_item['budgethoudervervanger'] = dbRegel['budgethoudervervanger']
        orderlist_item['activiteitenhoudervervanger'] = dbRegel['activiteitenhoudervervanger']
        orderlist.append(orderlist_item)

    return orderlist

#TODO use model.regel.add function (it is exactly the same!)
"""
.check_table_exists(table)
    input: table as str
    output: Boolean
"""
def check_table_exists(table):
    results = db.query("SHOW TABLES LIKE '" + table + "'")
    if len(results) == 0:
        return False
    return True

#TODO use model.regel.add function (it is exactly the same!)
"""
.add(table, fields, rows)
    input: table as str, fields as list of str, rows as list of str
    output: msg-queue as list of str
"""
def add(table, fields, rows):
    if not check_table_exists(table):
        fields_and_type = []
        for field in fields:
            sql_type = config["SAPkeys"]["types"][field]
            fields_and_type.append('`' + field + '` ' + sql_type)

        sql = "CREATE TABLE " + table + " (" + ', '.join(fields_and_type) + ");"
        results = db.query(sql)

#TODO use model.regel.add function (it is exactly the same!)
    row_chunks = __chunk_rows(rows, 10000)
    for rows in row_chunks:
        db.multiple_insert(table, values=rows)

# Cuts op the row list in multiple rows
# used by .add()
#TODO use model.regel.add function (it is exactly the same!)
def __chunk_rows(rows, chunk_size):
    for i in xrange(0, len(rows), chunk_size):
        yield rows[i:i + chunk_size]

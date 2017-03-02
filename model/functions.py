import web
from config import config

db = web.database(dbn='mysql', db=config["mysql"]["db"], user=config["mysql"]["user"], pw=config["mysql"]["pass"],
                  host=config["mysql"]["host"])


def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]


"""
.check_connection():
    input: none
    output: True/False
"""
def check_connection():
    try:
        results = db.query("SELECT 1")
    except Exception as e:
        return (False, e)

    return (True, '')


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


"""
.add(table, fields, rows)
    input: table as str, fields as list of str, rows as list of str
    output: msg-queue as list of str
"""
def add_items_to_db(table, fields, rows):
    if not check_table_exists(table):
        fields_and_type = []
        for field in fields:
            sql_type = config["SAPkeys"]["types"][field]
            fields_and_type.append('`' + field + '` ' + sql_type)

        sql = "CREATE TABLE " + table + " (" + ', '.join(fields_and_type) + ");"
        results = db.query(sql)

    MAX_CHUNKS = 5000  # ensures data for mysql < 1 mb
    row_chunks = __chunk_rows(rows, MAX_CHUNKS)
    for rows in row_chunks:
        db.multiple_insert(table, values=rows)

# Cuts op the row list in multiple rows
# used by .add()
def __chunk_rows(rows, chunk_size):
    for i in xrange(0, len(rows), chunk_size):
        yield rows[i:i + chunk_size]

"""
.count_table_others()
    input: None
    output: dict.value: number of entries as int, | -1 if table does not exist
            dict.key: tableName as str
"""
def count_tables_other():
    count = {}
    table_names = config["mysql"]["tables_other"].values()
    for table in table_names:
        if not check_table_exists(table):
            count[table] = -1
        else:
            try:
                results = db.query("SELECT COUNT(*) AS total_regels FROM %s" % (table))
            except Exception:
                results = None

            if results:
                count[table]= int(results[0].total_regels)
            else:
                count[table]= 0

    return count

def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]

def last_item_in_list(lst):
    return len(lst), lst[-1]

####################
# functions that are left over. Should still be re-assigned in model!
###################
# Moves a table in the db to a new one (renames!)
def move_table(table, target):
    if not check_table_exists(table):
        return False

    results = db.query("RENAME TABLE `sap`.`"+table+"` TO `sap`.`"+target+"`;")
    return True


# copyes a table in the db to target
def copy_table(table, target):
    if not check_table_exists(table):
        return False

    results = db.query("CREATE TABLE `sap`.`"+target+"` LIKE `sap`.`"+table+"`;")
    results = db.query("INSERT `sap`.`"+target+"` SELECT * FROM  `sap`.`"+table+"`;")
    return True


### SQL INJECTION POSSIBLE.. STRIP/VALUES FOR VALUES!
def create_table(table, fields):
    fieldsAndType = []
    for field in fields:
        sqlType = config["SAPkeys"]["types"][field]
        fieldsAndType.append('`'+field + '` ' + sqlType)

    sql = "CREATE TABLE " + table + " (" + ', '.join(fieldsAndType) + ");"
    results = db.query(sql)


# inserts multiple rows into the db.
# Splits up the rows in bunches of 10k to prevent
# timeout of the mysqldb
def insert_into_table(table, rows):
# used for debugging when a row makes the mysql db crash
    rowChunks = chunk_rows(rows, 10000)
    for rows in rowChunks:
        db.multiple_insert(table, values=rows)


# Cuts op the row list in multiple rows
def chunk_rows(rows, chunkSize):
    for i in xrange(0, len(rows), chunkSize):
        yield rows[i:i+chunkSize]

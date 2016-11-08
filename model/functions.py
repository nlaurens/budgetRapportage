def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]


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



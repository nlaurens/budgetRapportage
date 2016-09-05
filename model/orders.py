import glob
import os


"""
.available()
    input: None
    output: {'<order>': <name of order>}
"""
def available():
    orders = {}
    orders['test'] = 'dit is een test order'

    import csv
    with open('data/tmp-orders.dat', 'r') as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0].isdigit():
                order = int(row[0])
                descr = ''.join(e for e in row[1] if e.isalnum() or e ==' ').strip()
                orders[order] = descr
    return orders

def get_name(order_search):
    for order, descr in available().iteritems():
        if order == order_search:
            return descr

    return 'name not found'



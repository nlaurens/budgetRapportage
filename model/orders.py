import glob
import os


"""
.available()
    input: None
    output: {'<order>': <name of order>}
"""
def available():
    orders = {}
    orders['TEST'] = 'dit is een test order'

    import csv
    with open('tmp-orders.dat', 'r') as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            orders[row[0]] = row[1]

    return orders


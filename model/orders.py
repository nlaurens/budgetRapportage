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
                orders[int(row[0])] = row[1]

    return orders


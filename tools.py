"""
General tools.
"""
import sys
import model
import os
import budget
#Converts the order groups exported by SAP to readible format that can be edited.

def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]

def convert_gb_sap_2_txt(path):
    print 'converteren grootboek SAP export naar txt'
    print 'file: %s' % path
    print dir(budget.ordergroep)
    return

    root = budget.ordergroep.load_sap_export(path)
    file = open(path + '-converted.dat', 'w')
    root.save_as_txt(file)
    file.close()

if __name__ == "__main__":
    if len(sys.argv) <2:
        print 'error no arguments given'
        print 'use tools.py <tool> <input>'
        print 'tools: '
        print '  # GBSAP2TXT <path file>'
    elif sys.argv[1] == 'GBSAP2TXT':
        convert_gb_sap_2_txt(sys.argv[2])

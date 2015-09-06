"""
General tools.
"""
import sys
import model
import os
import GrootBoekGroep
#Converts the order groups exported by SAP to readible format that can be edited.

def convert_gb_sap_2_txt(groep):
    OGs = model.loadOrdergroepen()
    for OG in OGs:
        if groep == os.path.split(OG)[1]:
            print 'converting ' + str(OG)
            root = GrootBoekGroep.load(OG)
            file = open(groep + '.dat', 'w')
            root.save_as_txt(file)
            file.close()

if __name__ == "__main__":

    if len(sys.argv) <2:
        print 'error no arguments given'
        print 'use tools.py <tool> <input>'
        print 'tools: '
        print '  # GBSAP2TXT <grootboekgroep>'
    elif sys.argv[1] == 'GBSAP2TXT':
        convert_gb_sap_2_txt(sys.argv[2])

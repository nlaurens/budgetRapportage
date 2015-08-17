""""

"""
import web
import model
import GrootBoekGroep
import GrootBoek
from config import config
from functions import moneyfmt, IpBlock
from decimal import *
import glob


# Test to see if there are regels containing ks that are not
# in a report (and therefore would not show up).
def ks_missing_in_report(ks):
    #Alle kostensoorten in geboekt,oligo en plan:
    KSAll = model.get_kosten_soorten()

    #Load de kostensoortengroep of the report
    KSgroepen = model.loadKSgroepen()
    grootboek = KSgroepen[ks]
    emptyGB = GrootBoek.load_empty(grootboek)
    KSreport = emptyGB.walk_tree(9999)

    print 'testing report: '+ grootboek
    # Compare the two, note that KSAll is a tuple containing KS for geboekt, obligo and plan.
    for KS in KSAll:
        for ks, descr in KS.iteritems():
            if not ks in KSreport:
                print 'ERROR' + ' - ' + str(ks) + ' DOES NOT EXISTS'            

    print 'test completed'
        

if __name__ == "__main__":
    #test if BFRE15 covers all of our boeking, obligo and plan regels
    ks_missing_in_report(0)


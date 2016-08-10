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
def ks_missing_in_report():
    msg = []
    ksDB = model.get_kosten_soorten()

    # loop over all kostensoortgroepen
    for ksGroepName in model.loadKSgroepen().keys():
        root = GrootBoek.load(ksGroepName)
        ksGroep = root.get_ks_recursive()
        print ksDB
        for ks in ksDB:
            if ks not in ksGroep:
                msg.append('WARNING kostensoort %s appears in DB but is not included in report %s' % (ks, ksGroepName))

    if not msg:
        msg = ['PASS']
    return msg

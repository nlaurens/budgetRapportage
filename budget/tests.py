import model
import grootboek

def run_tests():
    success = False
    msg = [ 'nothing implmented' ]


    return (success, msg)

# Test to see if there are regels containing ks that are not
# in a report (and therefore would not show up).
def ks_missing_in_report():
    msg = []
    success = True
    ksDB = model.get_kosten_soorten()

    # loop over all kostensoortgroepen
    for ksGroepName in model.loadKSgroepen().keys():
        root = GrootBoek.load(ksGroepName)
        ksGroep = root.get_ks_recursive()
        for ks in ksDB:
            if ks not in ksGroep:
                success = False
                msg.append('WARNING kostensoort %s appears in DB but is not included in report %s' % (ks, ksGroepName))

    return (success, msg)

"""
TODO
"""
class Regel():


    # All attributes of Regel should be initialized here
    # The rest of the code should not add any attributes.
    def __init__(self):
        # general attributes that should exist in all tiepes (SAPkeys in config)
        self.tiepe = None
        self.order = None
        self.ordernaam = None
        self.kostensoort = None
        self.kostensoortnaam = None
        self.kosten = None
        self.jaar = None
        self.periode = None

        #specific for 'salaris'
        self.personeelsnummer = None
        self.personeelsnaam = None
        self.schaal = None
        self.trede = None

        #specific for obligo
        self.omschrijving = None
        self.documentnummer = None


    def druk_af(self):
        print '* regel'
        for attribute, value in vars(self).iteritems():
            print '  ' + attribute + ': ' + str(value)
        print ''


    def copy(self):
        new = Regel()
        for attribute, value in vars(self).iteritems():
            try:
                setattr(new, attribute, value)
            except:
                print 'Warning something went wrong with Regel.copy'
                exit()
        return new

    # Tries to load all available attributes from the db.select result
    # Delete all remaining 'None' attributes to make sure Python gives
    # an error when using an attribute that is not loaded/set.
    def import_from_db_select(self, dbRegel, tiepe):
        self.tiepe = tiepe

        for attribute in vars(self):
            try:
                dbValue = dbRegel[attribute]
                setattr(self, attribute, dbValue)
            except:
                pass

        attributes_remove_list = []
        for attribute, value in vars(self).iteritems():
            if value == None:
                attributes_remove_list.append(attribute)

        for attribute in attributes_remove_list:
            delattr(self, attribute)


# Edit specif rules here. Returns list of regels
def specific_rules(regel):
    modifiedRegels = [regel] # one regel can be replaced by multiple hence the list.

    #Specific rules per tiepe
    if regel.tiepe == 'plan':
        regel.periode = 1
        regel.omschrijving = 'begroting'

    if regel.tiepe == 'obligo':
        # Prognose afschrijvingen omzetten in 1 obligo
        if regel.kostensoort == 432100:
            modifiedRegels = [] #Remove old regel from list, we will ad new ones
            digits = [int(s) for s in regel.omschrijving.split() if s.isdigit()]
            periodeleft = range(digits[-2],digits[-1]+1)
            bedrag = regel.kosten/len(periodeleft)
            omschrijving = regel.omschrijving.decode('ascii', 'replace').encode('utf-8')
            for periode in periodeleft:
                regelNew = regel.copy()
                regelNew.omschrijving = omschrijving + '-per. ' + str(periode)
                regelNew.periode = periode
                regelNew.kosten = bedrag
                modifiedRegels.append(regelNew)

    #if tiepe == 'obligo' or 'geboekt':
        #self.omschrijving = self.omschrijving.decode('ascii', 'replace').encode('utf-8')

    return modifiedRegels

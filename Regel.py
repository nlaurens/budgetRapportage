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


    def druk_af(self):
        print self.order
        print self.kostensoort
        print self.kosten
        print self.omschrijving


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
    def import_from_db_select(self, dbRegel, tiepe, config):
        for attribute in vars(self):
            try:
                dbValue = dbRegel[config["SAPkeys"][tiepe][attribute]]
                setattr(self, attribute, dbValue)
            except:
                pass

        attributes_remove_list = []
        for attribute, value in vars(self).iteritems():
            if value == None:
                attributes_remove_list.append(attribute)

        for attribute in attributes_remove_list:
            delattr(self, attribute)
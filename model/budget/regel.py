class Regel:
    # All attributes of Regel should be initialized here
    # The rest of the code should not add any attributes.
    def __init__(self):
        # general attributes that should exist in all tiepes (SAPkeys in config)
        self.tiepe = None
        self.ordernummer = None
        self.ordernaam = None
        self.kostensoort = None
        self.kostensoortnaam = None
        self.kosten = None
        self.jaar = None
        self.periode = None

        # specific for salaris-plan/obligo/geboekt
        self.personeelsnummer = None
        self.personeelsnaam = None
        self.payrollnummer = None
        self.schaal = None
        self.trede = None

        # specific for obligo
        self.omschrijving = None
        self.documentnummer = None

    def druk_af(self):
        print '* regel'
        for attribute, value in vars(self).iteritems():
            try:
                print '  ' + attribute + ': ' + str(value)
            except Exception:
                print '  ' + attribute + ': <not printable>'
        print ''

    def copy(self):
        new = Regel()
        for attribute, value in vars(self).iteritems():
            try:
                setattr(new, attribute, value)
            except Exception:
                print 'Warning something went wrong with Regel.copy'
                exit()
        return new

    # Tries to load all available attributes from the db.select result
    # Delete all remaining 'None' attributes to make sure Python gives
    # an error when using an attribute that is not loaded/set.
    def import_from_db_select(self, db_regel, tiepe):
        self.tiepe = tiepe

        for attribute in vars(self):
            try:
                db_value = db_regel[attribute]
                setattr(self, attribute, db_value)
            except Exception:
                pass

        attributes_remove_list = []
        for attribute, value in vars(self).iteritems():
            if value is None:
                attributes_remove_list.append(attribute)

        for attribute in attributes_remove_list:
            delattr(self, attribute)

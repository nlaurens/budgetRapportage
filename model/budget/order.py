class Order:
    # All attributes of Order should be initialized here
    # The rest of the code should not add any attributes.
    def __init__(self):
        # general attributes that should exist in all tiepes (SAPkeys in config)
        self.ordernummer = None
        self.ordernaam = None

        self.budgethouder = None
        self.budgethoudervervanger = None
        self.activiteitenhouder = None
        self.activiteitenhoudervervanger = None

        self.activiteitencode = None
        self.subactiviteitencode = None

    def druk_af(self):
        print '* order'
        for attribute, value in vars(self).iteritems():
            try: 
                print '  ' + attribute + ': ' + str(value)
            except:
                print '  ' + attribute + ': CANNOT DISPLAY ITEM'
        print ''

    def copy(self):
        new = Order()
        for attribute, value in vars(self).iteritems():
            try:
                setattr(new, attribute, value)
            except Exception:
                print 'Warning something went wrong with Order.copy'
                exit()
        return new

    # Tries to load all available attributes from the db.select result
    # Delete all remaining 'None' attributes to make sure Python gives
    # an error when using an attribute that is not loaded/set.
    def import_from_db_select(self, db_orders):

        for attribute in vars(self):
            try:
                db_value = db_orders[attribute]
                setattr(self, attribute, db_value)
            except Exception:
                pass

        attributes_remove_list = []
        for attribute, value in vars(self).iteritems():
            if value is None:
                attributes_remove_list.append(attribute)

        for attribute in attributes_remove_list:
            delattr(self, attribute)

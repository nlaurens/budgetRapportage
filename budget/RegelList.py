class RegelList:
    regels = []  # List of regels

    def __init__(self, regels=None):
        if regels is None:
            regels = []
        self.regels = regels

    '''
    Returns a dictionary of RegelList sorted out by a specific
    attributes in the regel.
    For example:
        split_by_regel_attributes(self, ['order', 'kostensoort'])
    will return:
        dict['order1']['kostensoort1'] = RegelList
        dict['order1']['kostensoort..'] = RegelList
        dict['order2']['kostensoort1'] = RegelList
        dict['order2']['kostensoort..'] = RegelList
        dict['order..']['kostensoort..'] = RegelList
    '''

    def split_by_regel_attributes(self, attributes_to_group):
        regelListDict = self.__split_by_regel_attribute(attributes_to_group.pop(0))

        if attributes_to_group:
            for key, regelListDictChild in regelListDict.iteritems():
                regelListDict[key] = regelListDictChild.split_by_regel_attributes(
                    list(attributes_to_group))  # list(..) creates a copy for recursion!

        return regelListDict

    def __split_by_regel_attribute(self, attribute_to_group):
        regelDict = {}
        # Sort out regels for each attribute to group
        for regel in self.regels:
            regel_key = getattr(regel, attribute_to_group)
            if regel_key not in regelDict:
                regelDict[regel_key] = []
            regelDict[regel_key].append(regel)

        # Replace the regel list with a RegelList class
        regelListDict = {}
        for key, regels in regelDict.iteritems():
            regelListDict[key] = RegelList(regels)

        return regelListDict

    def total(self):
        total = 0
        for regel in self.regels:
            total = total + regel.kosten

        return total

    def extend(self, regelListToAdd):
        self.regels = self.regels + regelListToAdd.regels

    def filter_regels_by_attribute(self, attribute, list_allowed):
        new_regels = []
        for regel in self.regels:
            if getattr(regel, attribute) in list_allowed:
                new_regels.append(regel)

        self.regels = new_regels
        return self

    def druk_af(self):
        for regel in self.regels:
            regel.druk_af()

    def count(self):
        return len(self.regels)

    # Returns a copy of the RegelList for recursion.
    def copy(self):
        return RegelList(self.regels)

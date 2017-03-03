class RegelList:
    regels = []  # List of regels

    def __init__(self, regels=None):
        if regels is None:
            regels = []
        self.regels = regels

    def split(self, attributes_to_group):
        '''
        Returns a dictionary of RegelList sorted out by a specific
        attributes in the regel.
        For example:
            split(self, ['order', 'kostensoort'])
        will return:
            dict['order1']['kostensoort1'] = RegelList
            dict['order1']['kostensoort..'] = RegelList
            dict['order2']['kostensoort1'] = RegelList
            dict['order2']['kostensoort..'] = RegelList
            dict['order..']['kostensoort..'] = RegelList
        '''
        regel_list_dict = self.__split(attributes_to_group.pop(0))

        if attributes_to_group:
            for key, regel_list_dict_child in regel_list_dict.iteritems():
                regel_list_dict[key] = regel_list_dict_child.split(
                    list(attributes_to_group))  # list(..) creates a copy for recursion!

        return regel_list_dict

    def __split(self, attribute_to_group):
        regel_dict = {}
        # Sort out regels for each attribute to group
        for regel in self.regels:
            regel_key = getattr(regel, attribute_to_group)
            if regel_key not in regel_dict:
                regel_dict[regel_key] = []
            regel_dict[regel_key].append(regel)

        # Replace the regel list with a RegelList class
        regel_list_dict = {}
        for key, regels in regel_dict.iteritems():
            regel_list_dict[key] = RegelList(regels)

        return regel_list_dict

    def total(self):
        total = 0
        for regel in self.regels:
            total = total + regel.kosten

        return total

    def extend(self, regel_list_to_add):
        self.regels = self.regels + regel_list_to_add.regels

    def sort(self, attribute):
        self.regels.sort(key=lambda x: getattr(x, attribute), reverse=True)

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

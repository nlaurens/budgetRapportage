class RegelList():


    def __init__(self, regels):
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
            for key, regelListDictChild  in regelListDict.iteritems():
                regelListDict[key] = regelListDictChild.split_by_regel_attributes(list(attributes_to_group)) #list(..) creates a copy for recursion!

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


    def extend(self, regelsToAdd):
        self.regels = self.regels + regelsToAdd.regels


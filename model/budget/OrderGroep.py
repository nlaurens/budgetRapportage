class OrderGroep:
    def __init__(self, name, descr, level, parent):
        self.name = name
        self.descr = descr
        self.parent = parent
        self.level = level #Depth starts at 1
        self.children = []

        self.orders = {}  # list that holds all orders

    def flat_copy(self):
        flat = OrderGroep(self.name, 'Flat %s' % self.descr, 1, '')
        flat.orders = self.list_orders_recursive()
        return flat

    def add_order(self, order, descr):
        self.orders[order] = descr

    def add_child(self, child):
        self.children.append(child)

    def regel(self):
        print '*' * self.level + ' ' + self.name + ' (' + self.descr + ')'

    def druk_af(self):
        print 'ordergroep ' + self.name + ' (level ' + str(self.level) + ') - ' + self.descr

        if self.parent != '':
            print 'belongs to parent: ' + self.parent.name

        if self.orders:
            print 'contains the following orders:'
            print self.orders

        if self.children:
            print 'and has children:'
            for child in self.children:
                print child.name

        print ''

    def lower_level_parent(self, level):
        if self.level < level:
            return self
        else:
            return self.parent.lower_level_parent(level)

    def walk_tree(self, maxdepth):
        if self.level <= maxdepth:
            # Use drukAf() or regel voor debugging.
            self.druk_af()
            # self.regel()
            for child in self.children:
                child.walk_tree(maxdepth)

    def walk_levels(self):
        levels = {self.level}
        if self.children:
            for child in self.children:
                levels.update(child.walk_levels())

        return levels

    # returns a list of all nodes from self
    # that have requested level
    def find_level(self, level):
        levels = []
        for child in self.children:
            levels = levels + child.find_level(level)

        if self.level == level:
            levels.append(self)

        return levels

    def find(self, name):
        if self.name == name:
            return self
        elif self.children:
            for child in self.children:
                result = child.find(name)
                if result != '':
                    return result
        return ''

    # Creates a list of all levels in the tree
    # for example: [1, 5, 12, 40]
    def list_levels(self, levels):
        for child in self.children:
            levels = child.list_levels(levels)

        if self.level not in levels:
            levels.append(self.level)

        return levels

    # runs through the tree and adjusts levels
    # using the translate dictionary
    def correct_levels(self, translate):
        for child in self.children:
            child.correct_levels(translate)

        self.level = translate[self.level]

        return

    # normalizes the depth of levels to 1,2,3,..
    def normalize_levels(self):
        levels = sorted(self.list_levels([]))

        i = 0
        translate_table = {}
        for level in levels:
            translate_table[level] = i
            i += 1

        self.correct_levels(translate_table)

        return

    # returns: [ {descr:name} ] for all groepen in nodes
    def list_groepen_recursive(self):
        groepen = {}
        groepen[self.descr] = self.name
        for child in self.children:
            groepen.update(child.list_groepen_recursive())
        return groepen

    # return [ {descr:name} ] for all orders in nodes
    def list_orders_recursive(self):
        orders = self.orders.copy()
        for child in self.children:
            orders.update(child.list_orders_recursive())
        return orders

    def save_as_txt(self, fileHandle):
        lvl = self.level + 1
        sp = (lvl - 1) * '    '
        head = lvl * '#'

        fileHandle.write(sp + head + self.name + ' ' + self.descr + '\n')
        if self.orders:
            for order, descr in self.orders.iteritems():
                fileHandle.write(sp + ' ' + str(order) + ' ' + descr + '\n')

        fileHandle.write('\n')

        for child in self.children:
            child.save_as_txt(fileHandle)


def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]

# We don't use sap exports anymore. Need to be converted first!
def load(groepPath):
    root = ''
    f = open(groepPath, 'r')
    group = ''
    for line in f:
        line = line.strip()
        if line != '':
            if line[0] == '#':
                lvl = 0
                while line[lvl] == '#':
                    lvl += 1

                lvl -= 1
                sp = line.index(' ')
                name = line[lvl + 1:sp]
                descr = line[sp + 1:]
                if group == '':
                        group = OrderGroep(name, descr, lvl, '')
                        root = group
                else:
                    parent = group.lower_level_parent(lvl)
                    group = OrderGroep(name, descr, lvl, parent)
                    parent.add_child(group)
            else:
                sp = line.index(' ')
                order = line[:sp]
                descr = line[sp + 1:]
                group.add_order(int(order), descr)


    return root

# Only use for converting!
def load_sap_export(groepPath):
    print 'WARNING THIS SHOULD ONLY BE USED FOR CONVERTING SAP EXPORTS'
    root = ''
    f = open(groepPath, 'r')
    group = ''
    for line in f:
        line = line.replace('|', ' ')
        line = line.replace('--', '')
        line = line.split(' ')
        level, item = first_item_in_list(line)
        item = item.strip()
        descr = ' '.join(line[level + 1:]).strip()

        if item != '':
            if item.isdigit():
                if not descr.isdigit():
                    group.add_order(int(item), descr)
            elif group == '':
                group = OrderGroep(item, descr, level, '')
                root = group
            else:
                print 'GROUP %s - %s (%s)' % (level, item, descr)
                parent = group.lower_level_parent(level)
                group = OrderGroep(item, descr, level, parent)
                parent.add_child(group)

    return root

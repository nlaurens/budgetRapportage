import model


class OrderGroep():

    def __init__(self, name, descr, level, parent):
        self.name = name
        self.descr = descr
        self.parent = parent
        self.level = level
        self.children = []

        self.orders = {} #list that holds all orders

    def add_order(self, order, descr):
        self.orders[order] = descr

    def add_child(self, child):
        self.children.append(child)

    def regel(self):
        print '*' * self.level + ' ' + self.name + ' (' + self.descr + ')'

    def druk_af(self):
        print 'ordergroep ' + self.name + ' (level '+str(self.level)+') - ' + self.descr

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
            #self.regel()
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

    #return all orders in node and subnodes
    def list_orders_recursive(self):
        orders = self.orders.copy()
        for child in self.children:
            orders.update(child.list_orders_recursive())
        return orders


    def save_as_txt(self, file):
        lvl = self.level + 1
        sp = (lvl-1)*'    '
        head = lvl*'#'

        file.write(sp + head + self.name + ' ' + self.descr + '\n')
        if self.orders:
            for order, descr in self.orders.iteritems():
                file.write(sp + ' ' + str(order) + ' ' + descr+ '\n')

        file.write('\n')

        for child in self.children:
            child.save_as_txt(file)


def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]


def load(groep):
    groepen = model.loadOrderGroepen()
    path = groepen[groep]

    f = open(path, 'r')
    group = ''
    for line in f:
        line = line.strip()
        if line != '':
            if line[0] == '#':
                lvl = 0
                while line[lvl] == '#':
                    lvl += 1

                lvl = lvl -1
                sp = line.index(' ')
                name = line[lvl+1:sp]
                descr = line[sp+1:]
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
                descr = line[sp+1:]
                group.add_order(int(order), descr)

    return root


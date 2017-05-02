class KostensoortGroup:
    def __init__(self, name, descr, level, parent):
        self.name = name
        self.descr = descr
        self.parent = parent  # KostensoortGroup class
        self.level = level
        self.kostenSoorten = {}  # KS die bij deze node horen (uit kostensoortgroep)
        self.children = []  # list of kostensoortGroup classes

    def add_kostensoort(self, kostensoort, descr):
        self.kostenSoorten[kostensoort] = descr

    def add_child(self, child):
        self.children.append(child)

    def lower_level_parent(self, level):
        if self.level < level:
            return self
        else:
            return self.parent.lower_level_parent(level)

    # Finds a child and returns that child
    def find(self, name):
        if self.name == name:
            return self
        elif self.children:
            for child in self.children:
                result = child.find(name)
                if result is not None:
                    return result
        else:
            return None

    def walk_tree(self, maxdepth):
        "helper debug function"
        if self.level <= maxdepth:
            self.druk_af()
            for child in self.children:
                child.walk_tree(maxdepth)

    def druk_af(self):
        "helper debug function"
        print 'ksgroup ' + self.name + ' (level ' + str(self.level) + ') - ' + self.descr

        if self.parent != '':
            print 'belongs to parent: ' + self.parent.name

        if self.kostenSoorten:
            print 'contains the following kostensoorten:'
            print self.kostenSoorten

        if self.children:
            print 'and has children:'
            for child in self.children:
                print child.name

        print ''

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

    # Returns a dictionary of all ks from the whole tree
    def get_ks_recursive(self):
        ks = {}
        for child in self.children:
            ks.update(child.get_ks_recursive())

        ks.update(self.kostenSoorten)
        return ks

    def save_as_txt(self, filehandle):
        lvl = self.level + 1
        sp = (lvl - 1) * '    '
        head = lvl * '#'

        filehandle.write(sp + head + self.name + ' ' + self.descr + '\n')
        if self.kostenSoorten:
            for ks, descr in self.kostenSoorten.iteritems():
                filehandle.write(sp + ' ' + str(ks) + ' ' + descr + '\n')

        filehandle.write('\n')

        for child in self.children:
            child.save_as_txt(filehandle)


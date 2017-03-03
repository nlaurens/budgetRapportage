class KostensoortGroup:
    def __init__(self, name, descr, level, parent):
        self.name = name
        self.descr = descr
        self.parent = parent  # KostensoortGroup class
        self.level = level
        self.kostenSoorten = {}  # KS die bij deze node horen (uit kostensoortgroep)
        self.children = []  # list of kostensoortGroup classes

        self.regels = {}  # ['geboekt', 'obligo', 'plan'] = RegelList

        # We keep totals per node and tree to prevent running through it multiple
        # times when we display the tree in output or html.
        self.totaalNodePerKS = {}  # [geboekt, obligo, plan][<kostensoort] = <total kosten of node of that ks>
        self.totaalTree = {}  # [geboekt, obligo, plan] = <total of current node + children>

    def add_kostensoort(self, kostensoort, descr):
        self.kostenSoorten[kostensoort] = descr

    def add_child(self, child):
        self.children.append(child)

    def druk_af(self):
        print 'ksgroup ' + self.name + ' (level ' + str(self.level) + ') - ' + self.descr
        print 'totaal node: ' + str(self.totaalNodePerKS)
        print 'totaal tree: ' + str(self.totaalTree)

        if self.parent != '':
            print 'belongs to parent: ' + self.parent.name

        if self.kostenSoorten:
            print 'contains the following kostensoorten:'
            print self.kostenSoorten

        if self.regels:
            print 'contains the following regels:'
            for tiepe, regellist in self.regels.iteritems():
                print tiepe
                for regel in regellist.regels:
                    print '   ' + regel.omschrijving + ' - ' + str(regel.kosten) + ' - ' + regel.tiepe

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
            self.druk_af()
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

    # Assings regellist to all the children
    def assign_regels_recursive(self, regels):
        if not regels:  # No regels means we can directly exit
            return

        for child in self.children:
            child.assign_regels_recursive(regels)

        regels_by_type = regels.split(['tiepe'])  # plan, geboekt, obligo, etc.
        for regel_type, regels in regels_by_type.iteritems():
            filtered_regels = regels.copy()
            filtered_regels.filter_regels_by_attribute('kostensoort', self.kostenSoorten.keys())
            self.regels[regel_type] = filtered_regels

    # Set totals per key [obligo, plan, etc.], and per ks for each node
    def set_totals(self, periode_requested=range(0, 16)):
        self.totaalTree = {}
        self.totaalNodePerKS = {}
        self.totaalTree['geboekt'] = 0
        self.totaalTree['obligo'] = 0
        self.totaalTree['plan'] = 0

        # For each key [begroot, plan, ] split into ks and periode
        for key in self.regels.keys():
            regels_per_ks = self.regels[key].split(['kostensoort', 'periode'])

            # Walk over all ks, make sure there is a dict item
            for ks, regelsPerPeriode in regels_per_ks.iteritems():
                if key not in self.totaalNodePerKS:
                    self.totaalNodePerKS[key] = {}

                # walk over all periodes, make sure there is a dict item only if the period matches
                for periode, regellist in regelsPerPeriode.iteritems():
                    if periode in periode_requested:
                        if ks not in self.totaalNodePerKS[key]:
                            self.totaalNodePerKS[key][ks] = 0
                        self.totaalNodePerKS[key][ks] += regellist.total()
                        self.totaalTree[key] += regellist.total()

        # add childrens totaltree's
        for child in self.children:
            totaal_child_tree = child.set_totals(periode_requested=periode_requested)
            for key in totaal_child_tree.keys():
                self.totaalTree[key] += totaal_child_tree[key]

        return self.totaalTree

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

    def clean_empty_nodes(self):
        allchildrenempty = True

        emptychild = []
        for child in self.children:
            if child.clean_empty_nodes():
                emptychild.append(child)
            else:
                allchildrenempty = False

        for child in emptychild:
            self.children.remove(child)

        if not allchildrenempty:
            return False
        else:
            empty = True
            for key in self.regels.keys():
                if self.regels[key].count() > 0:
                    empty = False

            if empty:
                return True
            else:
                return False

    # Returns a list of all nodes that have no children (i.e. final nodes)
    def get_end_children(self, children):
        if self.children:
            for child in self.children:
                children.extend(child.get_end_children([]))
        else:
            return [self]

        return children

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


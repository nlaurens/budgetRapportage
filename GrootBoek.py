# TODO rename all fucntions that work on a tree with tree_...
# allf unctions that work on just the node node_..
import model


class GrootBoek():

    def __init__(self, name, descr, level, parent):
        self.name = name
        self.descr = descr
        self.parent = parent
        self.level = level
        self.kostenSoorten = {}
        self.children = []

        self.regels = {}

        self.totaalGeboektNode = {}  # Dict: kostensoort:totaal van de node
        self.totaalObligosNode = {}

        self.totaalGeboektTree = 0
        self.totaalObligosTree = 0

    def add_kostensoort(self, kostensoort, descr):
        self.kostenSoorten[kostensoort] = descr

    def add_child(self, child):
        self.children.append(child)

    def regel(self):
        #if (totals[0]+ totals[1]) != 0:
            #return '*' * self.level + ' ' + self.name + ' (' + self.descr + ') ' + str(self.totaalGeboektTree) + ' - ' + str(self.totaalObligosTree)
        return 'DEPRC. todo'

    def druk_af(self):
        print 'grootboek ' + self.name + ' (level '+str(self.level)+') - ' + self.descr
        print 'totaal node: ' + str(self.totaalGeboektNode) + ' | ' + str(self.totaalObligosNode)
        print 'totaal tree: ' + str(self.totaalGeboektTree) + ' | ' + str(self.totaalObligosTree)

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

    def lower_level_parent(self, level):
        if self.level < level:
            return self
        else:
            return self.parent.lower_level_parent(level)

    def html_tree(self, render, maxdepth, depth):
        depth += 1

        groups = []
        for child in self.children:
            groups.append(child.html_tree(render, maxdepth, depth))

        regelshtml = []

        for kostenSoort, regels in self.regels.iteritems():
            regelshtml.append(render.regels(self.name, kostenSoort, self.kostenSoorten[kostenSoort], self.totaalGeboektNode[kostenSoort], self.totaalObligosNode[kostenSoort], regels))

        if depth <= maxdepth:
            unfolded = True
        else:
            unfolded = False

        #render
        html = render.grootboekgroep(self.name, self.descr, groups, regelshtml, unfolded, self.totaalGeboektTree, self.totaalObligosTree, depth)

        return html

    def walk_tree(self, maxdepth):
        output = []
        if self.level <= maxdepth:
            # Use drukAf() voor debugging.
            #self.drukAf()
            output.append(self.regel())
            for child in self.children:
                output.extend(child.walk_tree(maxdepth))

        return output

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
        else:
            return ''

    def load_regels_recursive(self, order, geboektks, obligoks):
        for child in self.children:
            child.load_regels_recursive(order, geboektks, obligoks)

        ks = set(self.kostenSoorten.keys())
        for kostenSoort in (obligoks & ks):
            if kostenSoort in self.regels:
                self.regels[kostenSoort].extend(model.get_obligos(order, kostenSoort))
            else:
                self.regels[kostenSoort] = model.get_obligos(order, kostenSoort)

        for kostenSoort in (geboektks & ks):
            if kostenSoort in self.regels:
                self.regels[kostenSoort].extend(model.get_geboekt(order, kostenSoort))
            else:
                self.regels[kostenSoort] = model.get_geboekt(order, kostenSoort)

    def set_totals(self):
        geboekttotaal, obligostotaal = self.__totaal()

        for child in self.children:
            geboekt, obligos = child.set_totals()
            geboekttotaal += geboekt
            obligostotaal += obligos

        self.totaalGeboektTree = geboekttotaal
        self.totaalObligosTree = obligostotaal

        return geboekttotaal, obligostotaal

    def __totaal(self):
        geboekt = {}
        obligos = {}
        for kostenSoort, lijst in self.regels.iteritems():
            if not kostenSoort in obligos:
                obligos[kostenSoort] = 0
            if not kostenSoort in geboekt:
                geboekt[kostenSoort] = 0

            for regel in lijst:
                if regel.tiepe == 'Obligo':
                    obligos[kostenSoort] = obligos[kostenSoort] + regel.kosten
                elif regel.tiepe == 'Geboekt':
                    geboekt[kostenSoort] = geboekt[kostenSoort] + regel.kosten

        self.totaalGeboektNode = geboekt
        self.totaalObligosNode = obligos

        return sum(geboekt.itervalues()), sum(obligos.itervalues())

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
            if not self.regels:
                return True
            else:
                return False


def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]


def load_sap_export(path):
    f = open(path, 'r')
    group = ''
    for line in f:
        split = line.split("\t")
        if len(split) > 1:
            i, item = first_item_in_list(split)
            j, descr = last_item_in_list(split)

            item = item.rstrip()
            descr = descr.rstrip()
            if item.isdigit():
                group.add_kostensoort(int(item), descr)
            elif item != '>>> Interval leeg':
                if group == '':
                    group = GrootBoek(item, descr, i, '')
                    root = group
                else:
                    parent = group.lower_level_parent(i)
                    group = GrootBoek(item, descr, i, parent)
                    parent.add_child(group)

    return root


def load(order, grootboek):
    root = load_sap_export(grootboek)
    geboektks, obligoks = model.get_kosten_soorten(order)
    root.load_regels_recursive(order, set(geboektks), set(obligoks))

    root.clean_empty_nodes()
    root.set_totals()

    return root

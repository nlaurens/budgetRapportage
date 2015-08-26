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
        self.totaalPlanNode = {}

        self.totaalGeboektTree = 0
        self.totaalObligosTree = 0
        self.totaalPlanTree = 0

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
        print 'totaal node: ' + str(self.totaalPlanNode) + str(self.totaalGeboektNode) + ' | ' + str(self.totaalObligosNode)
        print 'totaal tree: ' + str(self.totaalPlanTree) + str(self.totaalGeboektTree) + ' | ' + str(self.totaalObligosTree)

        if self.parent != '':
            print 'belongs to parent: ' + self.parent.name

        if self.kostenSoorten:
            print 'contains the following kostensoorten:'
            print self.kostenSoorten

        if self.regels:
            print 'contains the following regels:'
            for ks, regels in self.regels.iteritems():
                print ks
                for regel in regels:
                    print '   '+ regel.omschrijving + ' - ' + str(regel.kosten) + ' - ' + regel.tiepe

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
        from functions import moneyfmt
        depth += 1

        groups = []
        for child in self.children:
            groups.append(child.html_tree(render, maxdepth, depth))

        regelshtml = []

        unfolded = False # Never show the details
        for kostenSoort, regels in self.regels.iteritems():
            plan = 0
            plan = moneyfmt(self.totaalPlanNode[kostenSoort])
            totaalGeboekt = moneyfmt(self.totaalGeboektNode[kostenSoort])
            totaalObligos = moneyfmt(self.totaalObligosNode[kostenSoort])
            for regel in regels:
                regel.kosten = moneyfmt(regel.kosten, places=2, dp='.')

            KSname = self.kostenSoorten[kostenSoort]
            KSname = str(kostenSoort) +' - ' + KSname.decode('ascii', 'replace').encode('utf-8')
            regelshtml.append(render.regels(self.name, kostenSoort, KSname, totaalGeboekt, totaalObligos, plan, regels, unfolded))

        if depth <= maxdepth:
            unfolded = True
        else:
            unfolded = False

        totaalPlan = moneyfmt(self.totaalPlanTree)
        totaalGeboekt = moneyfmt(self.totaalGeboektTree)
        totaalObligos = moneyfmt(self.totaalObligosTree)
        html = render.grootboekgroep(self.name, self.descr, groups, regelshtml, unfolded, totaalGeboekt, totaalObligos, totaalPlan, depth)

        return html

    def walk_tree(self, maxdepth):
        output = []
        if self.level <= maxdepth:
            # Use drukAf() voor debugging.
            self.druk_af()
            #output.append(self.regel())
            for child in self.children:
                child.walk_tree(maxdepth)
                #output.extend(child.walk_tree(maxdepth))


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

    def assign_regels_recursive(self, regelsGeboekt, regelsObligos, regelsPlan):
        for child in self.children:
            child.assign_regels_recursive(regelsGeboekt, regelsObligos, regelsPlan)

        ksGeboekt = set(self.kostenSoorten.keys()) & set(regelsGeboekt.keys())
        ksObligos = set(self.kostenSoorten.keys()) & set(regelsObligos.keys())
        ksPlan = set(self.kostenSoorten.keys()) & set(regelsPlan.keys())

        regelsGeboektFiltered = { your_key: regelsGeboekt[your_key] for your_key in ksGeboekt}
        regelsObligosFiltered = { your_key: regelsObligos[your_key] for your_key in ksObligos}
        regelsPlanFiltered = { your_key: regelsPlan[your_key] for your_key in ksPlan}

        self.regels = regelsGeboektFiltered
        for kp, regels in regelsObligosFiltered.iteritems():
            if kp in self.regels:
                self.regels[kp].extend(regels)
            else:
                self.regels[kp] = regels

        for kp, regels in regelsPlanFiltered.iteritems():
            if kp in self.regels:
                self.regels[kp].extend(regels)
            else:
                self.regels[kp] = regels



    def set_totals(self):
        geboekttotaal, obligostotaal, plantotaal = self.__totaal()

        for child in self.children:
            geboekt, obligos, plan = child.set_totals()
            geboekttotaal += geboekt
            obligostotaal += obligos
            plantotaal += plan

        self.totaalGeboektTree = geboekttotaal
        self.totaalObligosTree = obligostotaal
        self.totaalPlanTree = plantotaal

        return geboekttotaal, obligostotaal, plantotaal

    def __totaal(self):
        geboekt = {}
        obligos = {}
        plan = {}
        for kostenSoort, lijst in self.regels.iteritems():
            if not kostenSoort in obligos:
                obligos[kostenSoort] = 0
            if not kostenSoort in geboekt:
                geboekt[kostenSoort] = 0
            if not kostenSoort in plan:
                plan[kostenSoort] = 0

            for regel in lijst:
                if regel.tiepe == 'Plan':
                    plan[kostenSoort] = plan[kostenSoort] + regel.kosten
                if regel.tiepe == 'Obligo':
                    obligos[kostenSoort] = obligos[kostenSoort] + regel.kosten
                elif regel.tiepe == 'Geboekt':
                    geboekt[kostenSoort] = geboekt[kostenSoort] + regel.kosten

        self.totaalGeboektNode = geboekt
        self.totaalObligosNode = obligos
        self.totaalPlanNode = plan

        return sum(geboekt.itervalues()), sum(obligos.itervalues()), sum(plan.itervalues())


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
            if not self.regels:
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

def first_item_in_list(lst):
    i = next(i for i, j in enumerate(lst) if j)
    return i, lst[i]


def last_item_in_list(lst):
    return len(lst), lst[-1]

def load_raw_sap_export(path):
    f = open(path, 'r')
    group = ''
    for line in f:
        line = line.replace('|', ' ')
        line = line.replace('--', '')
        line = line.split(' ')
        level, item = first_item_in_list(line)
        item = item.strip()
        descr = ' '.join(line[level+1:]).strip()

        if item!='':
            if item.isdigit():
                if not descr.isdigit():
                    group.add_kostensoort(int(item), descr)
            elif item != '>>>':
                if group == '':
                    group = GrootBoek(item, descr, level, '')
                    root = group
                else:
                    parent = group.lower_level_parent(level)
                    group = GrootBoek(item, descr, level, parent)
                    parent.add_child(group)

    return root

def load_empty(grootboek):
    root = load_raw_sap_export(grootboek)
    root.normalize_levels()

    return root

def load(order, grootboek, jaar, periodes):
    root = load_raw_sap_export(grootboek)

    ksGeboekt, ksObligos, ksPlan = model.get_kosten_soorten(order)
    regelsGeboekt = model.get_geboekt(jaar, periodes, order, ksGeboekt)
    regelsObligos = model.get_obligos(jaar, periodes, order, ksObligos)
    regelsPlan = model.get_plan(jaar, order, ksPlan)

    root.assign_regels_recursive(regelsGeboekt, regelsObligos, regelsPlan)
    root.normalize_levels()
    root.set_totals()

    return root

import glob
import os

from config import config
from budget import KostensoortGroup
from functions import first_item_in_list as first_item_in_list

"""
.available() 
    input: None 
    output: names of kostensoortgroups as a list of str
"""
def available():
    ksgroups = []
    for path in glob.glob("%s\*" % config['ksGroupsPath']):
        ksgroups.append( os.path.split(path)[1] )

    return ksgroups


"""
.load( name )
    input: name as str
    returns: KostenSoortGroup
"""
def load(ks_group_name):
    path = '%s\%s' % (config['ksGroupsPath'], ks_group_name)
    f = open(path, 'r')
    group = None
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
                    group.add_kostensoort(int(item), descr)
            elif item != '>>>':
                if group == None:
                    group = KostensoortGroup(item, descr, level, '')
                    ksgroup = group
                else:
                    parent = group.lower_level_parent(level)
                    group = KostensoortGroup(item, descr, level, parent)
                    parent.add_child(group)

    ksgroup.normalize_levels()
    return ksgroup

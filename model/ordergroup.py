import glob
import os

from config import config
from budget import OrderGroup
from model.functions import first_item_in_list

"""
.available() 
    input: None 
    output: names of ordergroups as a list of str
"""


def available():
    order_groups = []
    for path in glob.glob("%s\*" % config['orderGroupsPath']):
        order_groups.append(os.path.split(path)[1])

    return order_groups


"""
.load( name )
    input: name as str
    returns: OrderGroup
"""


def load(order_group_name):
    path = '%s\%s' % (config['orderGroupsPath'], order_group_name)
    f = open(path, 'r')

    group = None
    order_group = None
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
                if group is None:
                    group = OrderGroup(name, descr, lvl, '')
                    order_group = group
                else:
                    parent = group.lower_level_parent(lvl)
                    group = OrderGroup(name, descr, lvl, parent)
                    parent.add_child(group)
            else:
                sp = line.index(' ')
                order = line[:sp]
                descr = line[sp + 1:]
                group.add_order(int(order), descr)

    return order_group


"""
.load_sap( file_path )
    input: file_path as str
    returns: OrderGroup
"""


def load_sap(file_path):
    f = open(file_path, 'r')
    group = None
    ordergroup = None
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
            elif group is None:
                group = OrderGroup(item, descr, level, '')
                ordergroup = group
            else:
                print 'GROUP %s - %s (%s)' % (level, item, descr)
                parent = group.lower_level_parent(level)
                group = OrderGroup(item, descr, level, parent)
                parent.add_child(group)

    ordergroup.normalize_levels()
    return ordergroup

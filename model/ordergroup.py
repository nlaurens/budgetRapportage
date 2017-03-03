import glob
import os

from config import config
from budget import OrderGroup
from model.functions import first_item_in_list
import model.orders


def available(actcode_groups=False):
    """
    .available()
        input: actcode_groups as Bool (optional). Adds 'virtual' groups
            based on the activiteitencode of all the orders
        output: names of ordergroups as a list of str that are
                in the 'data\ordergroups' dir AND
                1 list per activiteitecode
    """
    order_groups = []
    for path in glob.glob("%s\*" % config['orderGroupsPath']):
        order_groups.append(os.path.split(path)[1])

    if actcode_groups:
        order_groups.extend(['Act.Code-%s' % s for s in model.orders.activiteitencodes()])

    return order_groups


def load(order_group_name):
    """
    .load( name )
        input: name as str
        returns: OrderGroup
    """
    path = '%s\%s' % (config['orderGroupsPath'], order_group_name)
    if os.path.isfile(path):
        order_group = load_from_file(path)
    else:
        order_group = load_from_orderlist(order_group_name)

    return order_group


def load_from_orderlist(act_code_load):
    """
    .load_from_orderlist
        input: activiteitencode as str
        output: model.budget.OrderGroup as instance
    """
    order_group = OrderGroup(act_code_load[-1], act_code_load, 0, '')
    orders_dict = model.orders.load().split(['activiteitencode'])
    print orders_dict
    print orders_dict[act_code_load[-1]]
    for order in orders_dict[act_code_load[-1]].orders:
        order_group.add_order(int(order.ordernummer), order.ordernaam)

    return order_group


def load_from_file(path):
    """
    .load_from_file
        input: path to file as str
        output: model.budget.OrderGroup instance
    """
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


def load_sap(file_path):
    """
    .load_sap( file_path )
        input: file_path as str
        returns: OrderGroup
    """
    f = open(file_path, 'r')
    group = None
    ordergroup = None
    for line in f:
        line = line.replace('|', ' ')
        line = line.replace('--', '')
        line = line.split(' ')
        level, item = first_item_in_list(line)
        item = ''.join(e for e in item if e.isalnum()).strip()
        descr = ' '.join(line[level + 1:]).strip()

        if item != '':
            if item.isdigit():
                if not descr.isdigit():
                    group.add_order(int(item), descr)
            elif group is None:
                group = OrderGroup(item, descr, level, '')
                ordergroup = group
            else:
                parent = group.lower_level_parent(level)
                group = OrderGroup(item, descr, level, parent)
                parent.add_child(group)

    ordergroup.normalize_levels()
    return ordergroup

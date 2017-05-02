import glob
import os

from config import config
from budget import KostensoortGroup
from model.functions import first_item_in_list as first_item_in_list


def available():
    """
    .available()
        input: None
        output: names of kostensoortgroups as a list of str
    """
    return config['ksgroup']['ksgroups'].keys()


def load(ks_group_name):
    """
    .load( name )
        input: name as str
        returns: KostenSoortGroup
    """
    path = os.path.join(config['ksgroup']['path'], ks_group_name)
    f = open(path, 'r')

    group = None
    ksgroup = None
    for line in f:
        line = line.strip()
        if line != '':
            if line[0] == '#':
                level = 0
                while line[level] == '#':
                    level += 1

                level -= 1
                sp = line.index(' ')
                name = line[level + 1:sp]
                descr = line[sp + 1:]
                if group is None:
                    group = KostensoortGroup(name, descr, level, '')
                    ksgroup = group
                else:
                    parent = group.lower_level_parent(level)
                    group = KostensoortGroup(name, descr, level, parent)
                    parent.add_child(group)
            else:
                sp = line.index(' ')
                name = line[:sp]
                descr = line[sp + 1:]
                group.add_kostensoort(int(name), descr)

    return ksgroup


def get_ks_map(ksgroup):
    """
    .get_ks_map( ksgroup )
        input: name as str
        returns: dictionary with ks as key 
    """
    raise NotImplemented


def get_color_map(ksgroup):
    """
    .get_ks_map( ksgroup )
        input: name as str
        returns: dictionary         
    """
    raise NotImplemented


def load_sap(ks_group_file):
    """
    .load_sap( name )
        input: name as str
        returns: KostenSoortGroup
    """
    f = open(ks_group_file, 'r')
    group = None
    ksgroup = None
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
                    group.add_kostensoort(int(item), descr)
            elif item != '>>>':
                if group is None:
                    group = KostensoortGroup(item, descr, level, '')
                    ksgroup = group
                else:
                    parent = group.lower_level_parent(level)
                    group = KostensoortGroup(item, descr, level, parent)
                    parent.add_child(group)

    ksgroup.normalize_levels()
    return ksgroup

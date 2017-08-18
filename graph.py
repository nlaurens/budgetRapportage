#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""
    Can be used to build graphs from the command line
"""
import web
web.config.debug = False  # Set to False for no ouput! Must be done before the rest

import controller.graph
import model
import argparse

# Taget = ordernummer/ksgroup
def graph(target, year, ksmap, colormap, output):
    graph = controller.graph.Graph()

    # set target and year
    graph.name = target
    graph.year = year

    # pre-load needed data/maps
    graph.ksmap = ksmap
    graph.colormap = colormap

    graph.load_data()

    # set output path
    graph.path = output

    # build and save graph
    graph.graph_realisatie()

def queue_all(years):
    graph_empty = controller.graph.Graph()
    graph_empty.load_maps()
    queue = []
    for og_file in model.ordergroup.available():
        ordergroup = model.ordergroup.load(og_file)
        orders = ordergroup.list_orders_recursive().keys()
        for year in years:
            for order in orders:
                queue.append({'output':'graphs/%s/realisatie/%s.png' % (year, order), 'target':order, 'year':year, 'ksmap':graph_empty.ksmap, 'colormap':graph_empty.colormap})

            for ordergroup in ordergroup.list_groups():
                queue.append({'output':'graphs/%s/realisatie/%s.png' % (year, '%s-%s' % (og_file, ordergroup.name)), 'target':'%s-%s' % (og_file, ordergroup.name), 'year':year, 'ksmap':graph_empty.ksmap, 'colormap':graph_empty.colormap})

    return queue

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='all, or a single ordernummer')
    args = parser.parse_args()

    if args.target == 'all':
        print 'Building queue...'
        years = [2016, 2017]
        queue = queue_all(years)
    else:
        print 'Building queue...'
        graph_empty = controller.graph.Graph()
        graph_empty.load_maps()
        queue = [{'output':'graphs/test.png', 'target':args.target, 'year':2017, 'ksmap':graph_empty.ksmap, 'colormap':graph_empty.colormap}]

    print 'building graphs...'
    total = len(queue)
    processed = 0
    for item in queue:
        graph(**item)
        processed +=1
        print 'processed %s %s (%s - %s)' % (item['year'], item['target'], processed, total)

    print 'done.'



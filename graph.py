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
import sys

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
    parser.add_argument('-a','--all', action='store_true', help='builds all ordergroups and orders in the groups')
    parser.add_argument('-o','--order', help='builds specific ordernummer')
    parser.add_argument('-og','--ordergroup', help='builds the specific ordergroup graph')
    parser.add_argument('-n','--name', help='forces graph to be build to <name>.png, can be used with -o or -og')
    parser.add_argument('-y','--year', default=2017, help='specifices year to build, can be used with -o or -og')

    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

    queue = []
    if args.all:
        print 'Preparing all ordergroups and orders...'
        years = [2016, 2017]
        queue = queue_all(years)
    elif args.order:
        order = args.order
        print 'Preparing single order ' + order
        year = args.year
        graph_empty = controller.graph.Graph()
        graph_empty.load_maps()
        if args.name:
            output = 'graphs/%s.png' % args.name
        else:
            output =  'graphs/%s/realisatie/%s.png' % (year, order)
        queue = [{'output':output, 'target':order, 'year':year, 'ksmap':graph_empty.ksmap, 'colormap':graph_empty.colormap}]
    elif args.ordergroup:
        ordergroup = args.ordergroup
        print 'Preparing single ordergroup ' + ordergroup
        year = args.year
        graph_empty = controller.graph.Graph()
        graph_empty.load_maps()
        if args.name:
            output = 'graphs/%s.png' % args.name
        else:
            output =  'graphs/%s/realisatie/%s.png' % (year, ordergroup)
        queue = [{'output':output, 'target':ordergroup, 'year':year, 'ksmap':graph_empty.ksmap, 'colormap':graph_empty.colormap}]
        
    print 'building graphs...'
    total = len(queue)
    processed = 0
    for item in queue:
        print 'processing %s %s' % (item['year'], item['target'])
        graph(**item)
        processed +=1
        print '  processed: %s - %s' % (processed, total)

    print 'done.'

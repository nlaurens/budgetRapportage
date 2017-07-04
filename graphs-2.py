#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')  # Forces matplotlib not to use any xwindows calls
import web

web.config.debug = False  # must be done before the rest.

import model.regels
import model.ordergroup
import model.ksgroup
import model.orders

from controller.functions import moneyfmt

import os
from config import config
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.patches import Rectangle

import Queue
import threading
import time

exitFlag = 0

class myThread (threading.Thread):
   def __init__(self, threadID, q):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.q = q
   def run(self):
      print "Starting %s" % self.threadID
      process_data(self.threadID, self.q)
      print "Exiting %s" % self.threadID

def process_data(threadID, q):
   while not exitFlag:
      queueLock.acquire()
      if not workQueue.empty():
          item = q.get()
          queueLock.release()

          if item['type'] == 'realisatie':
            graph_realisatie(item)
          elif item['type'] == 'overview':
            graph_overview(item)

          print "thread %s finished %s" % (threadID, item['type'])
      else:
          queueLock.release()

def format_table_row(self, row):
    str_row = []
    for value in row:
        if value == 0 or np.abs(value) < 0.5:
            str_row.append('')
        else:
            str_row.append(moneyfmt(value))

    return str_row

def graph_realisatie(item):
    print 'graph realisatie done'
    global color_map
    print color_map
    data = item['data']

    data_x = np.arange(1, 13)
    data_x_begroting = np.array([0, 12])
    data_y_begroting = np.array([0, data['begroting'] / 1000])
    data_y_resultaat = data['resultaat'] / 1000

    # Layout figure
    plt.figure(figsize=(12, 9))
    plt.title(data['title'], loc='right', fontsize=12)

    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.get_xaxis().tick_bottom()
    plt.xticks(np.arange(0, 13, 1.0), fontsize=16)
    plt.xlim(0.5, 12.51)
    plt.xticks([])
    plt.xlabel("")
    plt.axhline(0, color='black')

    ax.get_yaxis().tick_left()
    plt.yticks(fontsize=14)
    plt.ylabel("Spent (keur)", fontsize=18)

    legend = {}
    legend['data'] = []
    legend['keys'] = []

    # Plot data
    plot_resultaat = plt.plot(data_x, data_y_resultaat, 'ro-', lw=2)
    plot_begroting = plt.plot(data_x_begroting, data_y_begroting, 'k--')

    # setup legend
    legend['data'].append(plot_resultaat[0])
    legend['keys'].append("Realisatie (%s keur)" % moneyfmt(data_y_resultaat[-1]))
    legend['data'].append(plot_begroting[0])
    legend['keys'].append("Begroting (%s keur)" % moneyfmt(data['begroting'], keur=True))
    legend['data'].append(Rectangle((0, 0), 0, 0, alpha=0.0))
    overschot = data['begroting'] / 1000 - data_y_resultaat[-1]
    if overschot > 0:
        legend['keys'].append("Te besteden (%s keur)" % moneyfmt(overschot))
    else:
        legend['keys'].append("Overbesteed: (%s keur)" % moneyfmt(overschot))

    leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
    if data_y_resultaat[-1] < 0:
        leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
    leg.get_frame().set_linewidth(0.0)

    # Plot bars of baten/lasten!
    totaalbars = len(data['baten']) + len(data['lasten'])
    width = 1. / (totaalbars + 1)
    offset = (1 - totaalbars * width) / 2
    bar_nr = 0
    for name, data_y in data['baten'].iteritems():
        plot_baten_bars = plt.bar(data_x + width * bar_nr - 0.5 + offset, data_y / 1000, width,
                                    color=color_map['baten'][name])
        bar_nr += 1

    for name, data_y in data['lasten'].iteritems():
        plot_lasten_bars = plt.bar(data_x + width * bar_nr - 0.5 + offset, data_y / 1000, width,
                                    color=color_map['lasten'][name])
        bar_nr += 1

    # add table below the graph
    values = []
    values.append(format_table_row(data_y_resultaat))  # totaal

    begroting_per_maand = data['begroting'] / 12000
    residue_begroting_per_maand = data_y_resultaat - np.linspace(begroting_per_maand, 12 * begroting_per_maand,
                                                                    num=12)
    values.append(format_table_row(residue_begroting_per_maand))

    for data_key in ['baten', 'lasten']:
        for key, row in data[data_key].iteritems():
            data[data_key][key] = row / 1000
            values.append(format_table_row(data[data_key][key]))

    label_columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

    label_rows = []
    label_rows.extend(["Totaal"])
    label_rows.extend(["+/- Begroting"])
    label_rows.extend(data['baten'].keys())
    label_rows.extend(data['lasten'].keys())

    colors = []
    for key in data['baten'].keys():
        colors.extend([color_map['baten'][key]])

    for key in data['lasten'].keys():
        colors.extend([color_map['lasten'][key]])

    for key in data['baten'].keys():
        colors.extend([color_map['baten'][key]])

    if colors:
        colors = np.insert(colors, 0, [1, 1, 1, 1], 0)  # Hack for making sure color realisatie
        colors = np.insert(colors, 0, [1, 1, 1, 1], 0)  # Hack for making sure color realisatie
    else:
        colors = [[1, 1, 1, 1], [1, 1, 1, 1]]

    the_table = plt.table(cellText=values, rowLabels=label_rows, rowColours=colors,
                            colLabels=label_columns, loc='bottom', rowLoc='right')
    the_table.set_fontsize(14)
    the_table.scale(1, 2)

    # Add y-lines:
    for i in range(0, 15):
        plt.axvline(i + 0.5, color='grey', ls=':')

    return plt
    
    time.sleep(0.01)

def graph_overview(item):

    time.sleep(0.01)

def load_data(workQueue):
    print 'loading years'
    years_available = model.regels.years()
    years = []
    for year in years_available:
        if year <= config['currentYear'] and year > config['currentYear'] - 5:
            years.append(year)

    print 'pre-loading order- and ks list and color map'
    orderListDict = model.orders.load().split(['ordernummer'])
    ordergroups = {}
    for name in model.ordergroup.available():
        ordergroups[name] = model.ordergroup.load(name)

    graph_ks_group = config['graphs']['ksgroup']
    ksgroup_root = model.ksgroup.load(graph_ks_group)
    ks_map = {}

    global color_map
    color_map = {'baten': {}, 'lasten': {}}

    for tiepe in ['baten', 'lasten']:
        for ks_groups in config['ksgroup']['ksgroups'][graph_ks_group][tiepe]:
            for child in ksgroup_root.find(ks_groups).children:
                color_map[tiepe][child.descr] = {}
                for ks in child.get_ks_recursive():
                    ks_map[ks] = (tiepe, child.descr)

            colors_amount = max(len(color_map[tiepe]), 3)  # prevent white colors
            colors = {}
            colors['baten'] = plt.cm.BuPu(np.linspace(0.75, 0.1, colors_amount))
            colors['lasten'] = plt.cm.BuGn(np.linspace(0.75, 0.1, colors_amount))
            for i, key in enumerate(color_map[tiepe]):
                color_map[tiepe][key] = colors[tiepe][i]


    print 'start loading regels'
    orders = model.regels.orders()
    regels = {}
    regels['plan'] = model.regels.load(['plan'], years_load=years, orders_load=orders)
    regels['resultaat'] = model.regels.load(['geboekt', 'obligo'], years_load=years, orders_load=orders)

    # construct data dicts
    print 'start building data structures orders'
    plan_dict = regels['plan'].split(['ordernummer', 'jaar'])
    regels_dict = regels['resultaat'].split(['ordernummer', 'jaar', 'kostensoort', 'periode'])

    data = {}
    for order in orders:
        data[order] = {}
        for year in years:
            data[order][year] = {}
            if order not in orderListDict:
                data[order][year]['title'] = '%s-%s-%s' % (order, order, year)
            else:
                data[order][year]['title'] = '%s-%s-%s' % (
                    orderListDict[order].orders[0].ordernaam, order, year)
            try:
                data[order][year]['begroting'] = float(plan_dict[order][year].total())
            except:
                data[order][year]['begroting'] = 0
            data[order][year]['baten'] = {}
            data[order][year]['lasten'] = {}
            data[order][year]['resultaat'] = np.zeros(12)

            if order in regels_dict:
                if year in regels_dict[order]:
                    for ks, regels_periode in regels_dict[order][year].iteritems():
                        key = ks_map[ks][0]
                        name = ks_map[ks][1]

                        if name not in data[order][year][key]:
                            data[order][year][key][name] = np.zeros(12)

                        for periode, regels in regels_periode.iteritems():
                            if periode > 12:
                                periode = 12
                            total = float(regels.total())
                            data[order][year][key][name][periode - 1] += total
                            data[order][year]['resultaat'][periode - 1] += total

            data[order][year]['resultaat'] = np.cumsum(data[order][year]['resultaat'])

    data_orders = data

    print 'start building data structures groups'
    data_orders = data_orders
    data = {}

    for name, ordergroup in ordergroups.iteritems():
        data[name] = {}
        for group in ordergroup.list_groups():
            data[name][group.name] = {}
            for year in years:
                data[name][group.name][year] = {}
                data[name][group.name][year]['title'] = '%s-%s-%s' % (group.descr, group.name, year)
                data[name][group.name][year]['begroting'] = 0
                data[name][group.name][year]['baten'] = {}
                data[name][group.name][year]['lasten'] = {}
                data[name][group.name][year]['resultaat'] = np.zeros(12)

                # add subgroup values
                for subgroup in group.children:
                    data[name][group.name][year]['begroting'] += data[name][subgroup.name][year]['begroting']
                    data[name][group.name][year]['resultaat'] += data[name][subgroup.name][year]['resultaat']

                    for key in ['baten', 'lasten']:
                        for ksgroup, row in data[name][subgroup.name][year][key].iteritems():
                            if ksgroup not in data[name][group.name][year][key]:
                                data[name][group.name][year][key][ksgroup] = row.copy()
                            else:
                                data[name][group.name][year][key][ksgroup] += row

                # add orders from this group
                for order in group.orders:
                    if order in data_orders:
                        data[name][group.name][year]['begroting'] += data_orders[order][year]['begroting']
                        data[name][group.name][year]['resultaat'] += data_orders[order][year]['resultaat']
                        for key in ['baten', 'lasten']:
                            for ksgroup, row in data_orders[order][year][key].iteritems():
                                if ksgroup not in data[name][group.name][year][key]:
                                    data[name][group.name][year][key][ksgroup] = row.copy()
                                else:
                                    data[name][group.name][year][key][ksgroup] += row
    data_groups = data

    print 'building queu orders'
    for order in orders:
        for year in years:
            realisatie = {'type':'realisatie', 'data':data_orders[order][year], 'year':year}
            workQueue.put(realisatie)

            overview = {'type':'overview', 'data':data_orders[order], 'year':year}
            workQueue.put(overview)



if __name__ == "__main__":
    queueLock = threading.Lock()
    workQueue = Queue.Queue()
    threads = []
    threadID = 1

    #TODO UNCOMMENT
    # Create new threads
    for tName in range(0,5):
       thread = myThread(threadID, workQueue)
       thread.start()
       threads.append(thread)
       threadID += 1

    # Fill the queue
    queueLock.acquire()
    load_data(workQueue)
    totalQueue = workQueue.qsize()
    print 'releasing queu and starting to work'
    queueLock.release()

    #TODO UNCOMMENT
    # Wait for queue to empty
    while not workQueue.empty():
        print 'Processing (%s/%s) - ' % (totalQueue - workQueue.qsize(), totalQueue)
        time.sleep(.1)
        pass
    
    # Notify threads it's time to exit
    exitFlag = 1
    
    # Wait for all threads to complete
    for t in threads:
       t.join()
    print "Exiting Main Thread"

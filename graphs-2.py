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
          data = q.get()
          queueLock.release()
          #print "%s processing %s" % (threadID, data['type'])
      else:
          queueLock.release()
      time.sleep(0.05)

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

    color_map = color_map
    ks_map = ks_map

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

    print 'start building data structures orders'
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
    print 'releasing queu and starting to work'
    #for word in nameList:
    #    item = {'type':'test', 'data':word, 'year':2017}
    #    workQueue.put(item)
    queueLock.release()

    #TODO UNCOMMENT
    # Wait for queue to empty
    while not workQueue.empty():
       pass
    
    # Notify threads it's time to exit
    exitFlag = 1
    
    # Wait for all threads to complete
    for t in threads:
       t.join()
    print "Exiting Main Thread"

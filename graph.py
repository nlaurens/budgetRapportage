""""
Usage
    $ python graph.py <year>
    use * for all years

NOTES

    only shows >|500| euro in table

TODO


"""
import web
web.config.debug = False #must be done before the rest.

import model.regels
import model.ordergroup
import model.ksgroup
import model.orders

from controller.functions import moneyfmt

import os
from config import config
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pylab as pylab
import sys
from matplotlib.patches import Rectangle

class Graph:
    def __init__(self, years, orders, ordergroups, regels):
        self.years = years  # [<year>,..]
        self.orders = orders  # [<order>,..]
        self.ordergroups = ordergroups   # { <name>:<regellist>, ..}
        self.regels = regels  # {'plan':<regellist>, 'realisatie':<regellist>}
        self.last_update = model.regels.last_update()
        self.order_names = model.orders.available()

        ksgroup_root = model.ksgroup.load(config['graphs']['ksgroup'])
        ks_map = {}
        color_map = {'baten': {}, 'lasten': {}}
        for tiepe in ['baten', 'lasten']:
            for child in ksgroup_root.find(config['graphs'][tiepe]).children:
                color_map[tiepe][child.descr] = {}
                for ks in child.get_ks_recursive():
                    ks_map[ks] = (tiepe, child.descr)

            colors_amount = max(len(color_map[tiepe]), 3)  # prevent white colors
            colors = {}
            colors['baten'] = plt.cm.BuPu(np.linspace(0.75, 0.1, colors_amount))
            colors['lasten'] = plt.cm.BuGn(np.linspace(0.75, 0.1, colors_amount))
            for i, key in enumerate(color_map[tiepe]):
                color_map[tiepe][key] = colors[tiepe][i]

        self.color_map = color_map
        self.ks_map = ks_map


    def render_test_graphs(self):
        data = {}
        data['test'] = {}
        for year in self.years:
            data['test'][year] = {}
            data['test'][year]['title'] = '%s-%s-%s' % (self.order_names['test'], 'test', year)
            data['test'][year]['begroting'] = float(100000)
            data['test'][year]['baten'] = {}
            data['test'][year]['lasten'] = {}
            data['test'][year]['resultaat'] = np.zeros(12)

            for key in ['baten', 'lasten']:
                for name in self.color_map[key].keys():
                    if name not in data['test'][year][key]:
                        data['test'][year][key][name] = np.zeros(12)

                    for periode in range (1, 13):
                        total = np.random.randint(1666)  # 12*<0-1666> = 100k
                        data['test'][year][key][name][periode-1] += total
                        data['test'][year]['resultaat'][periode-1] += total

            data['test'][year]['resultaat'] = np.cumsum(data['test'][year]['resultaat'])

        # realisatie graphs:
        total_graphs = 10
        count = 0
        for year in self.years:
            plt = self.graph_realisatie(data['test'][year])
            count += 1
            print 'rendered %s year %s (%.2f%%)' % ('test', year, (count/total_graphs)*100.)
            self.save_fig(plt, year, 'realisatie', 'test')
            plt.close()

            plt = self.graph_overview(year, data['test'])
            self.save_fig(plt, year, 'overview', 'test')
            plt.close()
            count += 1
            print 'rendered overview (%.2f%%)' % ((count/total_graphs)*100.)

    def render_graphs(self):

        # build graphs
        total_graphs = float(len(self.years)*len(self.orders)) * 2  # overview/realisatie
        for name, ordergroup in self.ordergroups.iteritems():
            total_graphs += float(len(self.years)*len(ordergroup.list_groups()))*2

        count = 0
        print 'start rendering graphs - total: %s' % total_graphs
        for order in self.orders:
            for year in self.years:
                plt = self.graph_realisatie(self.data_orders[order][year])
                self.save_fig(plt, year, 'realisatie', order)
                plt.close()
                count += 1
                print 'rendered %s realisatie - year %s (%.2f%%)' % (order, year, (count/total_graphs)*100.)

                plt = self.graph_overview(year, self.data_orders[order])
                self.save_fig(plt, year, 'overview', order)
                plt.close()
                count += 1
                print 'rendered %s overview   - year %s (%.2f%%)' % (order, year, (count/total_graphs)*100.)

        for name, ordergroup in self.ordergroups.iteritems():
            for group in ordergroup.list_groups():
                for year in self.years:
                    plt = self.graph_realisatie(self.data_groups[name][group.name][year])
                    self.save_fig(plt, year, 'realisatie', '%s-%s' % (name, group.name))
                    plt.close()
                    count += 1
                    print 'rendered %s-%s realisatie - year %s (%.2f%%)' % (name, group.name, year, (count/total_graphs)*100.)

                    plt = self.graph_overview(year, self.data_groups[name][group.name])
                    self.save_fig(plt, year, 'overview', '%s-%s' % (name, group.name))
                    plt.close()
                    count += 1
                    print 'rendered %s-%s overview   - year %s (%.2f%%)' % (name, group.name, year, (count/total_graphs)*100.)

    def construct_data_orders(self):
        plan_dict = self.regels['plan'].split(['ordernummer', 'jaar'])
        regels_dict = self.regels['resultaat'].split(['ordernummer', 'jaar', 'kostensoort', 'periode'])

        data = {}
        for order in orders:
            data[order] = {}
            for year in self.years:
                data[order][year] = {}
                if order not in self.order_names:
                    data[order][year]['title'] = '%s-%s-%s' % (order, order, year)
                else:
                    data[order][year]['title'] = '%s-%s-%s' % (self.order_names[order], order, year)
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
                            key = self.ks_map[ks][0]
                            name = self.ks_map[ks][1]

                            if name not in data[order][year][key]:
                                data[order][year][key][name] = np.zeros(12)

                            for periode, regels in regels_periode.iteritems():
                                if periode > 12:
                                    periode = 12
                                total = float(regels.total())
                                data[order][year][key][name][periode-1] += total
                                data[order][year]['resultaat'][periode-1] += total

                data[order][year]['resultaat'] = np.cumsum(data[order][year]['resultaat'])

        self.data_orders = data

    #overview: 1 kolom extra in elke tabel en daarin het grafiekje van de jaren zetten zodat het goed te zien is
    # grafiek: x = jan/dec, y = 0 tot 100% realisatie t.o.v. begroting (dus 1 lijn begroting stippel de rest in kleurtjes
    # met in legenda eronder de absolute getallen in realisatie
    def graph_overview(self, render_year, data):
        data_x = np.arange(1,13)
        data_y = {}
        for year in self.years:
            if year <= render_year:
                data_y[year] = data[year]['resultaat']/1000

        # title graph
        title = data[render_year]['title']

        # Layout figure
        plt.figure(figsize=(12, 9))
        plt.title(title, loc='right', fontsize=12)

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

        #Plot data and legend
        table_data = []
        plot_resultaat = {}
        plot_begroting = {}
        color_count = 0
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        for year in self.years:
            if year <= render_year:
                table_data.append([
                    year,
                    moneyfmt(data[year]['begroting'], keur=True),
                    moneyfmt(data[year]['resultaat'][-1], keur=True),
                    moneyfmt(data[year]['begroting']-data[year]['resultaat'][-1], keur=True),
                    ])
                begroting = np.array([data[year]['begroting']/1000,data[year]['begroting']/1000])

                color = colors[color_count]
                color_count += 1
                plot_resultaat[year] = plt.plot(data_x, data_y[year], 'o-', lw=2, color=color)
                plot_begroting[year] = plt.plot(np.array([0,12]), np.array(begroting), '--', color=color)
                legend['data'].append(plot_resultaat[year][0])
                legend['keys'].append("%s" % (year))


        leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
        leg.get_frame().set_linewidth(0.0)

        table_labels=("Year", "Budget", "Spent", "+/-")
        the_table = plt.table(cellText=table_data,colLabels=table_labels,loc='bottom', rowLoc='right')
        the_table.set_fontsize(14)
        the_table.scale(1,2)
        return plt

    def graph_realisatie(self, data):
        data_x = np.arange(1,13)
        data_x_begroting = np.array([0, 12])
        data_y_begroting = np.array([0, data['begroting']/1000])
        data_y_resultaat = data['resultaat']/1000

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

        #Plot data
        plot_resultaat = plt.plot(data_x, data_y_resultaat, 'ro-', lw=2)
        plot_begroting = plt.plot(data_x_begroting, data_y_begroting, 'k--')

        # setup legend
        legend['data'].append(plot_resultaat[0])
        legend['keys'].append("Realisatie (%s keur)" % moneyfmt(data_y_resultaat[-1]))
        legend['data'].append(plot_begroting[0])
        legend['keys'].append("Begroting (%s keur)" % moneyfmt(data['begroting'], keur=True))
        legend['data'].append(Rectangle( (0,0),0,0, alpha=0.0))
        overschot = data['begroting']/1000 - data_y_resultaat[-1]
        if overschot>0:
            legend['keys'].append("Te besteden (%s keur)" % moneyfmt(overschot))
        else:
            legend['keys'].append("Overbesteed: (%s keur)" % moneyfmt(overschot))

        leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
        if data_y_resultaat[-1] < 0:
            leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
        leg.get_frame().set_linewidth(0.0)

        # Plot bars of baten/lasten!
        totaalbars = len(data['baten'])+len(data['lasten'])
        width= 1./(totaalbars+1)
        offset = (1-totaalbars*width)/2
        bar_nr = 0
        for name, data_y in data['baten'].iteritems():
            plot_baten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, data_y/1000,  width, color=self.color_map['baten'][name])
            bar_nr += 1

        for name, data_y in data['lasten'].iteritems():
            plot_lasten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, data_y/1000,  width, color=self.color_map['lasten'][name])
            bar_nr += 1

        # add table below the graph
        values = []
        values.append(self.format_table_row(data_y_resultaat))

        for data_key in ['baten', 'lasten']:
            for key, row in data[data_key].iteritems():
                data[data_key][key] = row / 1000
                values.append(self.format_table_row(data[data_key][key]))

        label_columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

        label_rows = []
        label_rows.extend(["Totaal"])
        label_rows.extend(data['baten'].keys())
        label_rows.extend(data['lasten'].keys())

        colors = []
        for key in data['baten'].keys():
            colors.extend([self.color_map['baten'][key]])

        for key in data['lasten'].keys():
            colors.extend([self.color_map['lasten'][key]])

        for key in data['baten'].keys():
            colors.extend([self.color_map['baten'][key]])

        if colors:
            colors = np.insert(colors, 0, [1,1,1,1], 0) #Hack for making sure color realisatie
        else:
            colors = [[1,1,1,1]]


        the_table = plt.table(cellText=values, rowLabels=label_rows, rowColours=colors,
                            colLabels=label_columns, loc='bottom', rowLoc='right')
        the_table.set_fontsize(14)
        the_table.scale(1,2)


        #Add y-lines:
        for i in range(0,15):
            plt.axvline(i+0.5, color='grey', ls=':')

        return plt

    def format_table_row(self, row):
        str_row = []
        for value in row:
            if value == 0 or np.abs(value) < 0.5:
                str_row.append('')
            else:
                str_row.append(moneyfmt(value))

        return str_row

    def save_fig(self, plt, year, tiepe, name):
        path_graph = config['graphs']['path'] + '%s/%s/' % (year, tiepe)
        if not os.path.isdir(path_graph):
            os.makedirs(path_graph)
        plt.savefig(path_graph + '%s.png' % str(name), bbox_inches='tight')



    def construct_data_groups(self):
        assert self.data_orders is not None, "graph.data_orders not set"

        data_orders = self.data_orders
        data = {}

        for name, ordergroup in self.ordergroups.iteritems():
            data[name] = {}
            for group in ordergroup.list_groups():
                data[name][group.name] = {}
                for year in self.years:
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
        self.data_groups = data

if __name__ == "__main__":
    # used for testing graphs:
    test = False

    #from controller import functions
    # Run it: $python server.py <year>/*
    valid_input = False
    if len(sys.argv) == 2:
        years_available = model.regels.years()
        if str(sys.argv[1]) == '*':
            years = years_available
            valid_input = True
        elif str(sys.argv[1]) == 'TEST':
            years = years_available
            test = True
            valid_input = True
        else:
            year = int(sys.argv[1])
            if year in years_available:
                years = [year]
                valid_input = True

    if valid_input:
        print 'start loading regels'
        orders = model.regels.orders()

        ordergroups = {}
        for name in model.ordergroup.available():
            ordergroups[name] = model.ordergroup.load(name)

        regels = {}
        regels['plan'] = model.regels.load(years_load=years, orders_load=orders, table_names_load=['plan'])
        regels['resultaat'] = model.regels.load(years_load=years, orders_load=orders, table_names_load=['geboekt', 'obligo'])


        graph = Graph(years, orders, ordergroups, regels)
        # construct data dicts
        print 'start building data structures'
        graph.construct_data_orders()
        graph.construct_data_groups()
        if test:
            graph.render_test_graphs()
        else:
            graph.render_graphs()
    else:
        print 'error in arguments'
        print 'use graph.py <jaar>'
        print '* for all years'
        print 'or TEST for just a test graph'

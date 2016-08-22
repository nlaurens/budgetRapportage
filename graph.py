""""
Usage
    $ python graph.py <order/group>
    use * for all orders

NOTES

    only shows >|500| euro in table

TODO

# Bij het maken van een enkele graph de naam van de order uit een config tabel halen (bestaat nog niet!)
# Kijken naar de if/else structuur van de argv parser. Als je geen argumenten geeft krijg je fout melding .
# Afronding: alleen doen bij visualisatie, niet in export naar files en totalen niet optellen uit afgeronde cijfers.
# Algemeen
    Jaaroverzicht maken -> per jaar doorlinken naar de onderstaande rapportages.
    Hash alle plaatjes met username om te voorkomen dat je ze zo van elkaar kan zien
    Als ordergroep geen groepen eronder heeft gaat het mis. (dus b.v. 2008A3 zo uitdraaien)
# Allow the script to accept 'year' as an input param so we can build any year as well
# Store figs in the proper directory 'static/xxx'
# fig1:

# fig2:
    remove_pieces: check of er slechts 1 piece verwijdert wordt. Want dan kan je hem beter laten staan!
    Als het totaal 0 is moet je toch een pie chart maken met 1 piecie.
# fig3:
    y-labels kleurtje geven (want als niet begroot is, is ie sowieso rood..)

#overview: 1 kolom extra in elke tabel en daarin het grafiekje van de jaren zetten zodat het goed te zien is
# grafiek: x = jan/dec, y = 0 tot 100% realisatie t.o.v. begroting (dus 1 lijn begroting stippel de rest in kleurtjes
# met in legenda eronder de absolute getallen in realisatie

"""
import web
web.config.debug = False #must be done before the rest.

import model.regels
import model.ordergroup
import model.ksgroup

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

        # TODO naar config and also define colors there! So each cat. has always the same color!!
        ksgroup_root = model.ksgroup.load('BFRE15')
        ks_map = {}
        #TODO to 1 function that uses 'baten': [bfre, xx.], 'lasten;[BFRExx,..']
        for child in ksgroup_root.find('BFRE15BT00').children:
            for ks in child.get_ks_recursive():
                ks_map[ks] = ('baten', child.descr)

        for child in ksgroup_root.find('BFRE15E02').children:
            for ks in child.get_ks_recursive():
                ks_map[ks] = ('baten', child.descr)

        for child in ksgroup_root.find('BFRE15LT00').children:
            for ks in child.get_ks_recursive():
                ks_map[ks] = ('lasten', child.descr)

        self.ks_map = ks_map

    def build_graphs(self):
        # construct data dicts
        print 'start building data structures'
        data_orders = self.construct_data_orders()  
        data_groups = self.construct_data_groups(data_orders) 

        # build graphs
        total_graphs = float(len(self.years)*len(self.orders)) 
        for name, ordergroup in self.ordergroups.iteritems():
            total_graphs += float(len(self.years)*len(ordergroup.list_groups()))

        count = 0 
        print 'start rendering graphs - total: %s' % total_graphs

        for order in self.orders:
            # TODO
            #build_overview(order, data_orders)

            # realisatie graphs:
            for year in self.years:
                plt = self.graph_realisatie(data_orders[order][year])
                count += 1
                print 'rendered %s year %s (%.2f%%)' % (order, year, (count/total_graphs)*100.)
                self.save_fig(plt, year, 'realisatie', order)
                plt.close()

        for name, ordergroup in self.ordergroups.iteritems():
            for group in ordergroup.list_groups():
                #TODO
                #build_overview(group, data_groups)
                for year in self.years:
                    plt = self.graph_realisatie(data_groups[name][group.name][year])
                    count += 1
                    print 'rendered %s-%s year %s (%.2f%%)' % (name, group.name, year, (count/total_graphs)*100.)
                    self.save_fig(plt, year, 'realisatie', '%s-%s' % (name, group.name))
                    plt.close()


    def construct_data_orders(self):
        plan_dict = self.regels['plan'].split(['ordernummer', 'jaar'])
        regels_dict = self.regels['resultaat'].split(['ordernummer', 'jaar', 'kostensoort', 'periode'])

        data = {} 
        for order in orders:
            data[order] = {}
            for year in years:
                data[order][year] = {}
                data[order][year]['title'] = '%s-%s-%s' % ('dummy descr', order, year)  # TODO plot title
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

        return data

    def graph_realisatie(self, data):
        data_x = np.arange(1,13)
        data_x_begroting = np.array([1, 12])
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
        plt.ylabel("K euro", fontsize=18)

        legend = {}
        legend['data'] = []
        legend['keys'] = []

        colors = self.get_colors({'lasten':len(data['lasten']), 'baten':len(data['baten'])})
    
        #Plot data
        plot_resultaat = plt.plot(data_x, data_y_resultaat, 'ro-', lw=2) 
        plot_begroting = plt.plot(data_x_begroting, data_y_begroting, 'k--')
        
        # setup legend
    #TODO moneyfmt values in legend
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
            plot_baten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, data_y/1000,  width, color=colors[bar_nr])
            bar_nr += 1

        for name, data_y in data['lasten'].iteritems():
            plot_lasten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, data_y/1000,  width, color=colors[bar_nr])
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

        colors = np.insert(colors, 0, [1,1,1,1], 0) #Hack for making sure color realisatie

        the_table = plt.table(cellText=values, rowLabels=label_rows, rowColours=colors,
                            colLabels=label_columns, loc='bottom', rowLoc='right')
        the_table.set_fontsize(14)
        the_table.scale(1,2)

        #Add y-lines:
        for i in range(0,15):
            plt.axvline(i+0.5, color='grey', ls=':')

        return plt

    #TODO shouldn't we use money fmt and assume everything is a decimal?
    def format_table_row(self, row):
        str_row = []
        for value in row:
            if value == 0 or np.abs(value) < 0.5:
                str_row.append('')
            else:
                str_row.append(moneyfmt(value))

        return str_row

    def save_fig(self, plt, year, tiepe, name):
        path_graph = config['graphPath'] + '%s/%s/' % (year, tiepe)
        if not os.path.isdir(path_graph):
            os.makedirs(path_graph)
        plt.savefig(path_graph + '%s.png' % str(name), bbox_inches='tight')

    def get_colors(self, steps):
        colors_baten = plt.cm.BuGn(np.linspace(0.75, 0.1, steps['baten']))
        colors_lasten = plt.cm.BuPu(np.linspace(0.75, 0.1, steps['lasten']))
        return np.concatenate((colors_baten, colors_lasten), axis=0)


    def construct_data_groups(self, data_orders):
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
        return data

if __name__ == "__main__":
    #from controller import functions
    # Run it: $python server.py <year>/*
    valid_input = False
    if len(sys.argv) == 2:
        years_available = model.regels.years()
        if str(sys.argv[1]) == '*':
            years = years_available
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
        graph.build_graphs()
    else: 
        print 'error in arguments'
        print 'use graph.py <jaar>'
        print '* for all years'

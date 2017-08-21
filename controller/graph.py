import matplotlib
matplotlib.use('Agg')  # Forces matplotlib not to use any xwindows calls

from multiprocessing import Pool
import matplotlib.pyplot as plt
import numpy as np
import model.ksgroup
from functions import moneyfmt
from matplotlib.patches import Rectangle

from model.users import protected

import model.users

import web
import os
from config import config

"""
Graphs available:
    general URL: /graph/<year>/<type of graph>/<name of the graph>

    Note: Graph() is not a child of Controller-superclass as it doesn't render
          a page but returns directly an image to the browser.

    Note2: matplotlib is not 'thread' save - stuff stays global, mixes graphs
           and you get an error. Solution: use OO interface Matplotlib
"""


class Graph:
    def __init__(self):
        self.order_allowed = True  # TODO security
        self.path = None
        self.year = None
        self.graph_type = None
        self.name = None
        self.orderOrGroup = None

        self.plt = None

        self.colormap = None
        self.ksmap = None


    @protected()
    def GET(self, year, graph_type, name):
        self.year = year
        self.graph_type = graph_type
        self.name = name
        self.path = os.path.join(config['graphs']['path'], year, graph_type, name+'.png')

        if not self.authorized():
            raise web.notfound()

        if os.path.isfile(self.path):
            return self.serve_graph()
        else:
            self.create_graph()

        if os.path.isfile(self.path):
            return self.serve_graph()

        raise web.notfound()


    def authorized(self):
        types_allowed = ['realisatie']
        if not self.graph_type in types_allowed:
            return False

        # If user has no view or report perm. he has no business viewing graphs
        if not model.users.check_permission(['view']) and not model.users.check_permission(['report']):  
            return False

        try:
            order_allowed = int(self.name) in model.users.orders_allowed()
        except:
            order_allowed = False
        if not order_allowed: # Could still be an ordergroup instead of order...
            try:
                og_allowed = model.users.check_ordergroup(*model.ordergroup.decode(self.name))
            except:
                og_allowed = False

            if not og_allowed:
                return False

        try:
            year_allowed = int(self.year) in model.regels.years()
        except:
            year_allowed = False
        if not year_allowed:
            return False

        return True


    def serve_graph(self):
        web.header("Content-Type", "images/png")
        graph = open(self.path, "rb").read()
        # Debug: remove graph after serving so it gets rebuild every time
        # os.remove(self.path)

        return graph


    def create_graph(self):
        self.load_maps()
        self.load_data()

        if self.graph_type == 'realisatie':
            self.graph_realisatie()

    def load_maps(self):
        graph_ks_group = config['graphs']['ksgroup']
        ksgroup_root = model.ksgroup.load(graph_ks_group)
        self.ksmap = {}
        self.colormap = {'baten': {}, 'lasten': {}}

        for tiepe in ['baten', 'lasten']:
            for ks_groups in config['ksgroup']['ksgroups'][graph_ks_group][tiepe]:
                for child in ksgroup_root.find(ks_groups).children:
                    self.colormap[tiepe][child.descr] = {}
                    for ks in child.get_ks_recursive():
                        self.ksmap[ks] = (tiepe, child.descr)

                colors_amount = max(len(self.colormap[tiepe]), 3)  # prevent white colors
                colors = {}
                colors['baten'] = plt.cm.BuPu(np.linspace(0.75, 0.1, colors_amount))
                colors['lasten'] = plt.cm.BuGn(np.linspace(0.75, 0.1, colors_amount))
                for i, key in enumerate(self.colormap[tiepe]):
                    self.colormap[tiepe][key] = colors[tiepe][i]


    def format_table_row(self, row):
        str_row = []
        for value in row:
            if value == 0 or np.abs(value) < 0.5:
                str_row.append('')
            else:
                str_row.append(moneyfmt(value))

        return str_row


    def load_data(self):
        try:
            orders = [ int(self.name) ]
        except:
            og_file, og_group = model.ordergroup.decode(self.name)
            ordergroup = model.ordergroup.load(og_file)
            self.ordergroup = ordergroup.find(og_group)
            orders = self.ordergroup.list_orders_recursive().keys()

        regels = {}
        regels['plan'] = model.regels.load(['plan'], years_load=[self.year], orders_load=orders)
        regels['resultaat'] = model.regels.load(['geboekt', 'obligo'], years_load=[self.year], orders_load=orders)

        resultaat_ks_periode = regels['resultaat'].split(['kostensoort', 'periode'])

        data = {}
        data['title'] = '%s-%s-%s' % (self.name, self.name, self.year)  #TODO replace self.name with order descr if it is a single ordr

        try:
            data['begroting'] = float(regels['plan'].total())
        except:
            data['begroting'] = 0

        data['baten'] = {}
        data['lasten'] = {}
        data['resultaat'] = np.zeros(12)

        #prebuild ksgroup data structure to force fixed order (baten/lasten..)
        keys = ['baten', 'lasten']
        for key in keys:
            for ksgroup in self.colormap[key].keys():
                data[key][ksgroup] = np.zeros(12)

        for ks, resultaat_periode in resultaat_ks_periode.iteritems():
            key = self.ksmap[ks][0]
            name = self.ksmap[ks][1]

            for periode, regels in resultaat_periode.iteritems():
                if periode > 12:
                    periode = 12
                total = float(regels.total())
                data[key][name][periode - 1] += total
                data['resultaat'][periode - 1] += total

        data['resultaat'] = np.cumsum(data['resultaat'])

        # remove empty ksgroups
        keys = ['baten', 'lasten']
        empty_ksgroups = []
        for key in keys:
            for ksgroup, values in data[key].iteritems():
                if not np.any(values):
                    empty_ksgroups.append((key, ksgroup))

        for key, ksgroup in empty_ksgroups:
            del data[key][ksgroup]


        self.data = data


    def graph_realisatie(self):
        data_x = np.arange(1, 13)
        data_x_begroting = np.array([0, 12])
        data_y_begroting = np.array([0, self.data['begroting'] / 1000])
        data_y_resultaat = self.data['resultaat'] / 1000

        fig, ax = plt.subplots(figsize=(12,9))

        # Set layout
        ax.set_title(self.data['title'], loc='right', fontsize=12) 
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.set_xlim(0.5, 12.51)
        ax.set_xticks([])
        ax.hlines(0, 0, 13, color='black')

        ax.tick_params(axis='y', labelsize='14', left=True)
        ax.yaxis.set_label_text('Spent (keur)', size=18)

        legend = {}
        legend['data'] = []
        legend['keys'] = []

        # Plot data
        plot_resultaat = ax.plot(data_x, data_y_resultaat, 'ro-', lw=2)
        plot_begroting = ax.plot(data_x_begroting, data_y_begroting, 'k--')


        # setup legend
        legend['data'].append(plot_resultaat[0])
        legend['keys'].append("Realisatie (%s keur)" % moneyfmt(data_y_resultaat[-1]))
        legend['data'].append(plot_begroting[0])
        legend['keys'].append("Begroting (%s keur)" % moneyfmt(self.data['begroting'], keur=True))
        legend['data'].append(Rectangle((0, 0), 0, 0, alpha=0.0))
        overschot = self.data['begroting'] / 1000 - data_y_resultaat[-1]
        if overschot > 0:
            legend['keys'].append("Te besteden (%s keur)" % moneyfmt(overschot))
        else:
            legend['keys'].append("Overbesteed: (%s keur)" % moneyfmt(overschot))

        leg = ax.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
        if data_y_resultaat[-1] < 0:
            leg = ax.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
        leg.get_frame().set_linewidth(0.0)


        # Plot bars of baten/lasten!
        totaalbars = len(self.data['baten']) + len(self.data['lasten'])
        width = 1. / (totaalbars + 1)
        offset = (1 - totaalbars * width) / 2
        bar_nr = 0
        for name, data_y in self.data['baten'].iteritems():
            plot_baten_bars = ax.bar(data_x + width * bar_nr - 0.5 + offset, data_y / 1000, width,
                                        color=self.colormap['baten'][name])
            bar_nr += 1

        for name, data_y in self.data['lasten'].iteritems():
            plot_lasten_bars = ax.bar(data_x + width * bar_nr - 0.5 + offset, data_y / 1000, width,
                                        color=self.colormap['lasten'][name])
            bar_nr += 1

        # add table below the graph
        values = []
        values.append(self.format_table_row(data_y_resultaat))  # totaal

        begroting_per_maand = self.data['begroting'] / 12000
        residue_begroting_per_maand = data_y_resultaat - np.linspace(begroting_per_maand, 12 * begroting_per_maand,
                                                                        num=12)
        values.append(self.format_table_row(residue_begroting_per_maand))

        for data_key in ['baten', 'lasten']:
            for key, row in self.data[data_key].iteritems():
                self.data[data_key][key] = row / 1000
                values.append(self.format_table_row(self.data[data_key][key]))

        label_columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])

        label_rows = []
        label_rows.extend(["Totaal"])
        label_rows.extend(["+/- Begroting"])
        label_rows.extend(self.data['baten'].keys())
        label_rows.extend(self.data['lasten'].keys())

        colors = []
        for key in self.data['baten'].keys():
            colors.extend([self.colormap['baten'][key]])

        for key in self.data['lasten'].keys():
            colors.extend([self.colormap['lasten'][key]])

        for key in self.data['baten'].keys():
            colors.extend([self.colormap['baten'][key]])

        if colors:
            colors = np.insert(colors, 0, [1, 1, 1, 1], 0)  # Hack for making sure color realisatie
            colors = np.insert(colors, 0, [1, 1, 1, 1], 0)  # Hack for making sure color realisatie
        else:
            colors = [[1, 1, 1, 1], [1, 1, 1, 1]]

        the_table = ax.table(cellText=values, rowLabels=label_rows, rowColours=colors,
                                colLabels=label_columns, loc='bottom', rowLoc='right')
        the_table.set_fontsize(14)
        the_table.scale(1, 2)

        # Add y-lines:
        for i in range(0, 15):
            ax.axvline(i + 0.5, color='grey', ls=':')

        # Save the graph
        dir_graph = os.path.split(self.path)[0]
        if not os.path.isdir(dir_graph):
            os.makedirs(dir_graph)

        fig.savefig(self.path, bbox_inches='tight')
        plt.close(fig)

import matplotlib
matplotlib.use('Agg')  # Forces matplotlib not to use any xwindows calls

import matplotlib.pyplot as plt
import numpy as np
import model.ksgroup

import web
import os
from config import config

"""
Graphs available:
    general URL: /graph/<year>/<type of graph>/<name of the graph>
"""


class Graph:
    def __init__(self):
        self.order_allowed = True  # TODO security
        self.path = None
        self.year = None
        self.graph_type = None
        self.name = None
        self.plt = None
        self.colormap = None


    def GET(self, year, graph_type, name):
        self.year = year
        self.graph_type = graph_type
        self.name = name

        types_allowed = ['realisatie', 'overview']
        years_allowed = [2017]  # TODO add security by only adding years in db
        names_allowed = [ 'xx', 'yy']  #TODO add security by adding all groups/orders to this list

        if self.graph_type in types_allowed:
            self.path = os.path.join(config['graphs']['path'], year, graph_type, name+'.png')

            if os.path.isfile(self.path):
                return self.serve_graph()
            else:
                if self.create_graph():
                    return self.serve_graph()

        raise web.notfound()


    def serve_graph(self):
        web.header("Content-Type", "images/png")
        return open(self.path, "rb").read()


    def create_graph(self):
        self.create_colormap()
        self.plt = self.graph_test()
        self.save_fig(plt)

        return True


    def create_colormap(self):
        graph_ks_group = config['graphs']['ksgroup']
        ksgroup_root = model.ksgroup.load(graph_ks_group)
        ks_map = {}
        self.colormap = {'baten': {}, 'lasten': {}}

        for tiepe in ['baten', 'lasten']:
            for ks_groups in config['ksgroup']['ksgroups'][graph_ks_group][tiepe]:
                for child in ksgroup_root.find(ks_groups).children:
                    self.colormap[tiepe][child.descr] = {}
                    for ks in child.get_ks_recursive():
                        ks_map[ks] = (tiepe, child.descr)

                colors_amount = max(len(self.colormap[tiepe]), 3)  # prevent white colors
                colors = {}
                colors['baten'] = plt.cm.BuPu(np.linspace(0.75, 0.1, colors_amount))
                colors['lasten'] = plt.cm.BuGn(np.linspace(0.75, 0.1, colors_amount))
                for i, key in enumerate(self.colormap[tiepe]):
                    self.colormap[tiepe][key] = colors[tiepe][i]


    def save_fig(self, fig):
        dir_graph = os.path.split(self.path)[0]
        if not os.path.isdir(dir_graph):
            os.makedirs(dir_graph)

        self.plt.savefig(self.path, bbox_inches='tight')


    def graph_test(self):
        from matplotlib.mlab import bivariate_normal
        from numpy.core.multiarray import arange

        delta = 0.5

        x = arange(-3.0, 4.001, delta)
        y = arange(-4.0, 3.001, delta)
        X, Y = np.meshgrid(x, y)
        Z1 = bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
        Z2 = bivariate_normal(X, Y, 1.5, 0.5, 1, 1)
        Z = (Z1 - Z2) * 10

        fig = plt.figure(figsize=(10, 5))

        ax1 = fig.add_subplot(111)
        extents = [x.min(), x.max(), y.min(), y.max()]
        im = ax1.imshow(Z,
                        interpolation='spline36',
                        extent=extents,
                        origin='lower',
                        aspect='auto')
        ax1.contour(X, Y, Z, 10, colors='k')

        return fig


    def graph_realisatie(item):
        data = item['data']

        data_x = np.arange(1, 13)
        data_x_begroting = np.array([0, 12])
        data_y_begroting = np.array([0, data['begroting'] / 1000])
        data_y_resultaat = data['resultaat'] / 1000

        # Layout figure
        plt.figure(figsize=(12, 9))
        plt.title(data['title'], loc='right', fontsize=12)

        #TODO crashes when using multiple plots
        # look at fix: - using OO of matplotlib 
        # https://stackoverflow.com/questions/31719138/matplotlib-cant-render-multiple-contour-plots-on-django 
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
                                        color=self.colormap['baten'][name])
            bar_nr += 1

        for name, data_y in data['lasten'].iteritems():
            plot_lasten_bars = plt.bar(data_x + width * bar_nr - 0.5 + offset, data_y / 1000, width,
                                        color=self.colormap['lasten'][name])
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
            colors.extend([self.colormap['baten'][key]])

        for key in data['lasten'].keys():
            colors.extend([self.colormap['lasten'][key]])

        for key in data['baten'].keys():
            colors.extend([self.colormap['baten'][key]])

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

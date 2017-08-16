import matplotlib
matplotlib.use('Agg')  # Forces matplotlib not to use any xwindows calls

import matplotlib.pyplot as plt
import numpy as np

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
        fig = self.graph_test()
        self.save_fig(fig)

        return True

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


    def save_fig(self, fig):
        path_graph = os.path.join(config['graphs']['path'], str(self.year), self.graph_type)
        if not os.path.isdir(path_graph):
            os.makedirs(path_graph)

        path_fig = os.path.join(path_graph, '%s.png'% str(self.name))

        fig.savefig(path_fig, bbox_inches='tight')

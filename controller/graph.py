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
        if graph_type == 'realisatie' or graph_type == 'overview':
            self.path = config['graphs']['path'] + '%s/%s/%s.png' % (year, graph_type, name)

        graph = self.serve_image()
        if graph:
            return graph
        else:
            raise web.notfound()

    def serve_image(self):
        if os.path.isfile(self.path):
            web.header("Content-Type", "images/png")
            return open(self.path, "rb").read()
        else:
            return None

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
            self.path = os.path.join(config['graphs']['path'], year, graph_type, name+'.png')

        if os.path.isfile(self.path):
            return self.serve_image()
        else:
            generated = True
            # Try to generate the image
            if generated:
                return self.serve_image()

        raise web.notfound()

    def serve_image(self):
        web.header("Content-Type", "images/png")
        return open(self.path, "rb").read()

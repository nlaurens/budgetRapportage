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

        if self.graph_type not in types_allowed:
            self.path = os.path.join(config['graphs']['path'], year, graph_type, name+'.png')

            if os.path.isfile(self.path):
                return self.serve_image()
            else:
                if self.create_image():
                    return self.serve_image()

        raise web.notfound()


    def serve_image(self):
        web.header("Content-Type", "images/png")
        return open(self.path, "rb").read()


    def create_image(self):

        return False

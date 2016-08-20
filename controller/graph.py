import web
import os
from config import config

"""
Graphs available:
    general URL: /graph/<user_hash>/<type of graph>/<name of the graph>

    realisatie:
    /graph/<userHash>/realisatie/<order/groupname>?year=<year>
    
"""
# Not a subclass of controller as that creates to much overhead
class Graph:
    def __init__(self):
        self.order_allowed = True  # TODO security
        self.path = None
        self.year_start = web.input(year_start=None)['year_start']
        self.year_stop = web.input(year_stop=None)['year_stop']

    #def GET(self, user_hash, graph_type, graph_name):
    def GET(self, user_hash, graph_type, graph_name):
        print 'hallo'
        print user_hash
        print graph_type
        print graph_name
        print self.year_start
        if graph_type == 'realisatie' and self.year_start:
            self.path = config['graphPath'] + '%s/%s/%s.png' % (self.year_start, graph_type, graph_name)
        elif graph_type == 'overview' and self.year_start and self.year_stop:
            self.path = config['graphPath'] + '%s/%s/%s-%s.png' % (self.year_start, graph_type, graph_name, self.year_stop)

        graph = self.serve_image()
        if graph:
            return graph
        else:
            raise web.notfound()

    def serve_image(self):
        print self.path
        if os.path.isfile(self.path):
            web.header("Content-Type", "images/png")  # Set the Header
            return open(self.path, "rb").read()
        else:
            return None

import web
import os
from config import config

# Not a subclass of controller as that creates to much overhead
class Graph:
    def GET(self, userHash, jaar, tiepe, order):
# TODO security
        order_allowed = True
        graph_path = config['graphPath'] + '%s/%s/%s.png' % (jaar, tiepe, order)

        if int(jaar) in range(1000, 9999):
            if os.path.isfile(graph_path):
                web.header("Content-Type", "images/png")  # Set the Header
                return open(graph_path, "rb").read()
        else:
            raise web.notfound()


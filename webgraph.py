import web
from config import config
import os

# Opens and returns a graph as a data stream
def return_graph(jaar, tiepe, order):
    orderAllowed = True
    graphPath = config['graphPath'] +'%s/%s/%s.png' % (jaar, tiepe, order)

    if int(jaar) in range(1000, 9999):
        if os.path.isfile(graphPath):
            web.header("Content-Type", "images/png") # Set the Header
            return open(graphPath,"rb").read()
    else:
        raise web.notfound()

# Creates url to graph
# tiepes: realisatie, bars, pie
# names: anything from group orders to order numbers.
def generate_url(userHash, jaar, tiepe, name):
    return ('/graph/%s/%s/%s/%s.png' % (userHash, jaar, tiepe, name))


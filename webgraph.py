import web
from config import config
import os

#TODO CHECK IF ORDER EXIST AND IS ACCESSIBLE FOR USER
def return_graph(jaar, tiepe, order):
    orderAllowed = True
    graphPath = config['graphPath'] +'%s/%s/%s.png' % (jaar, tiepe, order)

    if int(jaar) in range(1000, 9999) and orderAllowed: #security
        if os.path.isfile(graphPath):
            web.header("Content-Type", "images/png") # Set the Header
            return open(graphPath,"rb").read()
    else:
        raise web.notfound()

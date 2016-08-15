from controller import Controller
class Graph(Controller):
    def process_sub(self, jaar, tiepe, order):
        self.body =  'Dummy graph %s %s %s' % (jaar, tiepe, order)
        #return webgraph.return_graph(jaar, tiepe, order)

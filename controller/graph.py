from controller import Controller
class Graph(Controller):
    def process_sub(self, userHash, jaar, tiepe, order):
        auth_block_by_ip()
        auth_login(session, userHash, 'index')
        return webgraph.return_graph(jaar, tiepe, order)

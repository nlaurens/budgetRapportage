""""
TODO

# Hash alle plaatjes met username om te voorkomen dat je ze zo van elkaar
   kan zien.

# Alles abstraheren zodat je ook een grafiek van alle orders bij elkaar (of groepen bij elkaar) kan maken

"""
import model
import GrootBoek
import GrootBoekGroep
import os
from config import config
from functions import moneyfmt, IpBlock
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

class Graph:
    def __init__(self, jaar, order):

        # Get params
        details = 1 # 0 = just result, 1 = depth 1, 2 = depth 2 etc.
        KSgroep = 1
        maxdepth = 1

        KSgroepen = model.loadKSgroepen()
        grootboek = KSgroepen[KSgroep]
        sapdatum = config['lastSAPexport']
        reserves = model.get_reserves()

        begroting = model.get_plan_totaal(2015,order)
        line = {}

        X = range(1,15)
        for periode in X:
            root = GrootBoek.load(order, grootboek, jaar, [periode])
            totaal = ( (-1*(root.totaalGeboektTree + root.totaalObligosTree)))
            if periode == 1:
                resultaat = [totaal]
            else:
                resultaat.append(totaal)

            previous = 0 
            depth = 0
# TODO recursive function voor linen op de juist diepte
           # for child in root.children:

           #     if depth < 
           #     if subs:
           #         for subchild in child.children:
           #             totaal = ( (-1*(subchild.totaalGeboektTree + subchild.totaalObligosTree)))
           #             if periode == 1:
           #                 line[subchild.name] = [ totaal ]
           #             else:
           #                 line[subchild.name].append(totaal)
           #     else:
           #         totaal = ( (-1*(child.totaalGeboektTree + child.totaalObligosTree)))
           #         if periode == 1:
           #             line[child.name] = [ totaal ]
           #         else:
           #             line[child.name].append(totaal)

        plt.figure()
        if details > 0:
            i = 0 
            p = {}
            for name, Y in line.iteritems():
                p[i] = plt.bar(X, np.cumsum(Y)/1000, 0.35, color=cm.jet(1.*i/len(line)))
                i += 1

        p1 = plt.plot(X, np.cumsum(resultaat)/1000, 'r-', lw=2)
        p2 = plt.plot([0,12], [0,begroting/1000], 'k--', lw=2)

        plt.ylabel('KEuro')
        plt.xlabel('Periode 2015')
        plt.title(str(order))
        plt.legend( (p1[0], p2[0]), ('Resultaat', 'Begroting'))
        plt.savefig('data/figs/'+ str(order) + '.png')


if __name__ == "__main__":
    orders = model.get_orders()
    for order in orders:
        graph = Graph('2015', str(order))

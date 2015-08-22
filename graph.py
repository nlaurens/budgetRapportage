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

    def test_graphs():
    from matplotlib import cm
# Toevoegen 'prognose extrapolatie'
# Maken 1 mooie functie die begroting, totaal en 'bar'-plots door krijgt. (X as kan hij zelf verzinnen = 12)
# Assume (Y = 12 groot, etc.)
#TODO: periode 12,13,14,15 in 1x ophalen bij loaden
# TODO alleen tot periode 'NU' binnen halen en plotten voor resultaat en staafjes

    prognose = True
    details_flat = False
    details_stack = True
    table = True

    order = 2008101010
    begroting = 100000
    resultaat = np.array([0,5000, 5000, 10000, 20000, 0, 0, 30000, 0, 0, 0,0])
    lines = {}
    lines['baten1'] = np.array([0,-2500, 0, 0, 0, 0, 0, 0, -10000, 0, 0,0])
    lines['baten2'] = np.array([0,-2500, 0, 0, 0, 0, 0, 0, -5000, 0, 0,0])
    lines['kosten1'] = np.array([0,3333, 0, 3333, 6666, 0, 0, 15000, 0, 0, 0, 0])
    lines['kosten2'] = np.array([0,3333, 0, 3333, 6666, 0, 0, 15000, 0, 0, 0, 0])
    lines['kosten3'] = np.array([0,3333, 5000, 3333, 6666, 0, 0, 15000, 0, 0, 0, 0])

#Convert all to Keur:
    for key, line in lines.iteritems():
        lines[key] = lines[key]/1000
    begroting = begroting/1000
    resultaat = resultaat/1000

#Fit
    X = np.arange(1,13)
    resultaat = np.cumsum(resultaat)
    z = np.polyfit(X, resultaat, 1)
    p = np.poly1d(z)

#Layout figure
    plt.figure()
    plt.figure(figsize=(12, 9))
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xticks(np.arange(0, 13, 1.0), fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel("Month", fontsize=18)
    plt.ylabel("K euro", fontsize=18)
    plt.xlim(0, 12)

    legend = {}
    legend['data'] = []
    legend['keys'] = []

#Plot data
    plt.title(str(order))
    p1 = plt.plot(X, resultaat, 'ro-', lw=2)
    p2 = plt.plot([0,12], [0,begroting], 'k--', lw=3)

    legend['data'].append(p1[0])
    legend['keys'].append("Realisatie")
    legend['data'].append(p2[0])
    legend['keys'].append("Begroting")

    if prognose:
        p3 = plt.plot([0,12], p([0,12]))
        legend['data'].append(p3[0])
        legend['keys'].append("Prognose")

    if details_flat:
        colors = plt.cm.BuPu(np.linspace(0, 0.5, len(lines)))
        width= 1./(len(lines)+1)
        offset = (1-len(lines)*width)/2
        i = 0
        for name, Y in lines.iteritems():
            p4 = plt.bar(X+width*i-0.5+offset, Y,  width, color=colors[i])
            i += 1
            legend['data'].append(p4[0])
            legend['keys'].append(name)

    if details_stack:
        colors = plt.cm.BuPu(np.linspace(0, 0.5, len(lines)))
        width= .36
        offset = (.36)/2
        y_offset_neg = 0
        y_offset_pos = 0

        i = 0
        for name, Y in lines.iteritems():
            y_offset = y_offset_neg*(np.array(Y<0)) + y_offset_pos*(np.array(Y>0))
            print y_offset
            p4 = plt.bar(X-offset, Y, width, bottom=y_offset, color=colors[i])
            i += 1
            legend['data'].append(p4[0])
            legend['keys'].append(name)
            #y_offset += (Y/1000)
            y_offset_neg += np.array(Y<0)*Y
            y_offset_pos += np.array(Y>0)*Y

    if table:
        # Plot bars and create text labels for the table
        y_offset = np.array([0.0] * len(lines))
        cell_text = []
        for row in range(len(lines)):
            cell_text.append(['%1.1f' % (x/1000.0) for x in y_offset])
        # Reverse colors and text labels to display the last value at the top.
        colors = colors[::-1]
        cell_text.reverse()

        columns = ('Freeze', 'Wind', 'Flood', 'Quake', 'Hail')
        rows = ['%d year' % x for x in (100, 50, 20, 10, 5)]
        the_table = plt.table(cellText=cell_text,
                        rowLabels=rows,
                        rowColours=colors,
                        colLabels=columns,
                        loc='bottom')#, bbox=[0.25, -0.5, 0.5, 0.3])
        #plt.subplots_adjust(left=0.2, bottom=0.5)

    plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=18, loc=2)
        # Add a table at the bottom of the axes


#save/show plot
    plt.show()
#plt.savefig('data/figs/'+ str(order) + '.png', bbox_inches="tight")



if __name__ == "__main__":
    orders = model.get_orders()
    for order in orders:
        graph = Graph('2015', str(order))

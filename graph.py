""""
TODO

# Jaaroverzicht maken -> per jaar doorlinken naar de onderstaande rapportages.

# Add pijl voor periode 12 tussen begroot en realisatie en zet text +xx keur of -yy keur (annotate is je vriend)
# Hash alle plaatjes met username om te voorkomen dat je ze zo van elkaar
   kan zien.
# Splitsen in 2 grootboekgroepen: baten (BFRE15EB) en lasten (BFRE15L). Dan is het echt clean.
# Aparte kleurenschema baten/lasten gebruiken
"""
import web
web.config.debug = False #must be done before the rest.

import model
import GrootBoek
import GrootBoekGroep
import os
from config import config
from functions import moneyfmt, IpBlock
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pylab as pylab
import sys

class Graph:
    def __init__(self):
        self.resultaat = None
        self.lines = {}
        self.begroot = {}
        pass

    def get_colors(self, valueType, steps):
        if valueType=='lasten':
            return plt.cm.BuPu(np.linspace(0.75, 0.25, steps))

        if valueType=='baten':
            return plt.cm.BuGn(np.linspace(0.75, 0.25, steps))

        sys.exit('unknown color map ' + valueType + ' in Graph.get_colors()') 


    def realisatie(self, params):
#TODO use self.vars throughout the function
        lines = self.lines.copy()
        resultaat = self.resultaat

        #Convert all to Keur:
        for key, line in lines.iteritems():
            lines[key] = np.array(lines[key])/1000
        begroting = np.cumsum(np.array(self.begroot['totaal']))/1000
        resultaat = np.array(resultaat)/1000

        #Fit
        X = np.arange(1,13)
        resultaat = np.cumsum(resultaat)
        z = np.polyfit(X, resultaat, 1)
        p = np.poly1d(z)

        #Layout figure
        plt.figure(figsize=(12, 9))

        ax = plt.subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.get_xaxis().tick_bottom()
        plt.xticks(np.arange(0, 13, 1.0), fontsize=16)
        plt.xlabel("Month", fontsize=18)
        plt.xlim(0.5, 12.51)

        ax.get_yaxis().tick_left()
        plt.yticks(fontsize=14)
        plt.ylabel("K euro", fontsize=18)

        legend = {}
        legend['data'] = []
        legend['keys'] = []

        colors = self.get_colors('lasten', len(lines))

        #Plot data
        p1 = plt.plot(X, resultaat, 'ro-', lw=2)
        p2 = plt.plot([0,12], [0,begroting], 'k--')
        legend['data'].append(p1[0])
        legend['keys'].append("Realisatie")
        legend['data'].append(p2[0])
        legend['keys'].append("Begroting")

        if params['show_prognose']:
            p3 = plt.plot([0,12], p([0,12]))
            legend['data'].append(p3[0])
            legend['keys'].append("Prognose")

        if params['show_details_flat']:
            width= 1./(len(lines)+1)
            offset = (1-len(lines)*width)/2
            i = 0
            for name, Y in lines.iteritems():
                if params['show_cumsum']:
                    Y = np.cumsum(Y)
                p4 = plt.bar(X+width*i-0.5+offset, Y,  width, color=colors[i])
                i += 1
                legend['data'].append(p4[0])
                legend['keys'].append(name)

        if params['show_details_stack']:
            width= .36
            offset = (.36)/2
            y_offset_neg = 0
            y_offset_pos = 0

            i = 0
            for name, Y in lines.iteritems():
                if params['show_cumsum']:
                    Y = np.cumsum(Y)
        #TODO if line switches from sign the offset doesn't work.
                y_offset = y_offset_neg*(np.array(Y<0)) + y_offset_pos*(np.array(Y>0))
                p4 = plt.bar(X-offset, Y, width, bottom=y_offset, color=colors[i])
                i += 1
                legend['data'].append(p4[0])
                legend['keys'].append(name)
                y_offset_neg += np.array(Y<0)*Y
                y_offset_pos += np.array(Y>0)*Y

        if params['show_table']:
            cell_text = []
            text = []
            for value in resultaat:
                text.append('%i'%value)
            cell_text.append(text)
            for key, line in lines.iteritems():
                text = []
                for value in line:
                    if value == 0:
                        text.append('')
                    else:
                        text.append('%i' % value)

                cell_text.append(text)

            columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
            rows = []
            rows.extend(["Cum. Resultaat"])
            rows.extend(lines.keys())
            colors = np.insert(colors, 0, [1,1,1,1], 0) #Hack for making sure colors line stay the same
            the_table = plt.table(cellText=cell_text,
                            rowLabels=rows,
                            rowColours=colors,
                            colLabels=columns,
                            loc='bottom')
            the_table.set_fontsize(14)
            the_table.scale(1,2)

            #Add y-lines:
            for i in range(0,15):
                plt.axvline(i+0.5, color='grey', ls=':')
            plt.axhline(0, color='black')
            plt.xticks([])
            plt.xlabel("")

        plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)

        return plt

    def baten_lasten_pie(self):
        lines = self.lines.copy()
        # Convert to keur
        for key, line in lines.iteritems():
            lines[key] = np.array(lines[key])/1000

        # The slices will be ordered and plotted counter-clockwise.
        baten_labels = []
        baten_values = []
        lasten_labels = []
        lasten_values = []
        for key, line in lines.iteritems():
            value = (np.sum(line))
            if value < 0:
                baten_values.append(np.absolute(value))
                baten_labels.append(key + '\n' + str(int(value)) + 'k eur')
            else:
                lasten_values.append(value)
                lasten_labels.append(key + '\n' + str(int(value)) + 'k eur')

        plt.figure(figsize=(12,5))
        #baten
        plt.subplot(121)
        pct= '%.f%%'
        if not baten_labels:
            baten_values = [ 1 ]
            baten_labels = ['0k eur']
            pct= ''

        colors = self.get_colors('baten', len(baten_labels))
        plt.pie(baten_values, labels=baten_labels, colors=colors,
                autopct=pct, shadow=True, startangle=90)
        plt.axis('equal')
        plt.title('Baten')

        #lasten
        plt.subplot(122)
        pct= '%.f%%'
        if not lasten_labels:
            lasten_values = [ 1 ]
            lasten_labels = ['0k eur']
            pct= ''

        colors = self.get_colors('lasten', len(lasten_labels))
        plt.pie(lasten_values, labels=lasten_labels, colors=colors,
                autopct=pct, shadow=True, startangle=90)
        plt.axis('equal')
        plt.title('Lasten')

        return plt


    def besteed_begroot(self):
        lines = self.lines.copy()
        begroot = self.begroot.copy()

        # Convert to keur
        for key, line in lines.iteritems():
            lines[key] = np.array(lines[key])/1000
        for key, line in begroot.iteritems():
            begroot[key] = np.array(begroot[key])/1000

        #data crunching
        names = list(lines.keys())
        realisatie = []
        residu = []
        color_res = []
        X_max = 0
        #Parse all lines
        for key, line in lines.iteritems():
            besteed = np.absolute(np.sum(line))
            realisatie.append(besteed)
            res = np.absolute(begroot[key]) - besteed

            if res <= 0 :
                color_res.append('pink')#pink
                X_max = max(X_max, (besteed))
            else:
                color_res.append('lightsage')
                X_max = max(X_max, (res+besteed))
            residu.append(res)

        #Parse all begrotingen that have no cost (i.e. no lines)
        # Note the totaal key is something we added manually and
        # Does not exist in the lines.
        for key, value in begroot.iteritems():
            if key not in lines and key != 'totaal':
                besteed = 0
                realisatie.append(besteed)
                res = np.absolute(begroot[key]) 

                if res <= 0 :
                    color_res.append('pink')#pink
                    X_max = max(X_max, (besteed))
                else:
                    color_res.append('lightsage')
                    X_max = max(X_max, (res+besteed))
                residu.append(res)
                names.append(key) #of gebruik insert(pos, key)
        
        #Layout figure
        fig, ax = plt.subplots(figsize=(12, 9))

        #ax = plt.subplot(111)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.get_xaxis().tick_bottom()
        plt.xticks(fontsize=16)
        plt.xlabel("K Euro", fontsize=18)
        plt.xlim(0, X_max*1.01)

        ax.get_yaxis().tick_left()

        #plot data
        pos = np.arange(len(realisatie))+0.5    # Center bars on the Y-axis ticks
        colors = self.get_colors('lasten', len(lines))

        realisatie_bars= plt.barh(pos, realisatie, align='center', height=0.5, color=colors)
        residu_bars = plt.barh(pos, residu, left=realisatie, align='center', height=0.5, color=color_res)

        #Labelling
        pylab.yticks(pos, names, fontsize=16)
        i = 0
        for rect in residu_bars:
            width = int(rect.get_width())

            if color_res[i]=='lightsage':
                xloc = 0.5*width + realisatie[i]
                rankStr = '+'+str(width)
            else:
                xloc = -0.4*width + realisatie[i]
                rankStr = '-'+str(width)

            xloc = min(xloc, X_max*1.01)
            yloc = rect.get_y()+rect.get_height()/2.0

            ax.text(xloc, yloc, rankStr,
                    verticalalignment='center', color='black', weight='bold')
            i +=1

        return plt

# TODO recursive function voor linen op de juist diepte
    def parse_node(self, root, subs, lines, begroot, periode):
        for child in root.children:
            if subs:
                for subchild in child.children:
                    totaal = ( ((subchild.totaalGeboektTree + subchild.totaalObligosTree)))
                    if periode == 1:
                        begroot[subchild.descr] =  subchild.totaalPlanTree
                        lines[subchild.descr] = [ totaal ]
                    else:
                        lines[subchild.descr].append(totaal)
            else:
                totaal = ( ((child.totaalGeboektTree + child.totaalObligosTree)))
                if periode == 1:
                    begroot[child.descr] = child.totaalPlanTree
                    lines[child.descr] = [ totaal ]
                else:
                    lines[child.descr].append(totaal)

        return lines, begroot

    def load(self, jaar, order):
        # Get params
        subs = True
        KSgroep = 1
        maxdepth = 1

        KSgroepen = model.loadKSgroepen()
        grootboek = [s for s in KSgroepen if "BFRE15E01" in s][0]
        sapdatum = config['lastSAPexport']

        begroot = {}
        lines = {}

        resultaat = []
        for periode in range(1,13):
            if periode == 12:
                periode == [12,13,14,15]
# TODO optimaliseer dit. 1x de grootboek laden en dan per node de totalen per periode ophalen
# ipv elke keer weer de mysql db raadplegen
            root = GrootBoek.load(order, grootboek, jaar, [periode])
            resultaat.append( (root.totaalGeboektTree + root.totaalObligosTree))
            begroot['totaal'] = root.totaalPlanTree

            lines, begroot = self.parse_node(root, subs, lines, begroot, periode)


        #Remove lines that only have 0's (don't check the sum, could be +50, -50)
#TODO refactor this into a function (double code, and will be tripple code with baten/lasten split)
        remove = []
        for key, line in lines.iteritems():
            if all(v == 0 for v in line):
                remove.append(key)

        for key in remove:
            del lines[key]
        # remove 0 lines that are not in lines (and also dont remove total)
        remove = []
        for key, value in begroot.iteritems():
            if value == 0 and key not in lines and key!='totaal':
                remove.append(key)

        for key in remove:
            del begroot[key]

        self.resultaat = resultaat
        self.lines = lines
        self.begroot = begroot

        if not lines:
            return False
        return True



if __name__ == "__main__":
    params = {}
    params['show_prognose'] = False
    params['show_cumsum'] = False
    params['show_details_flat'] = True
    params['show_details_stack'] = False
    params['show_table'] = True

    orders = model.get_orders()
    orders = [2008502040]

    for i, order in enumerate(orders):
        print '%i (%i out of %i - %i perc.)' % (order, i+1, len(orders), (float(i+1)/len(orders))*100)
        graph = Graph()
        if graph.load(2015, order):
            plt = graph.realisatie(params)
            plt.savefig('figs/'+str(order)+'-1.png', bbox_inches='tight')

            plt = graph.baten_lasten_pie()
            plt.savefig('figs/'+str(order)+'-2.png', bbox_inches='tight')

            plt = graph.besteed_begroot()
            plt.savefig('figs/'+str(order)+'-3.png', bbox_inches='tight')

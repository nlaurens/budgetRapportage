""""
NOTES

    only shows >500 euro in table

TODO

# Algemeen
    Jaaroverzicht maken -> per jaar doorlinken naar de onderstaande rapportages.
    Hash alle plaatjes met username om te voorkomen dat je ze zo van elkaar kan zien
    1x de grootboek laden en dan per node de totalen per periode ophalen ipv per periode grootboek laden (mysql stress)

# fig1:
    realisatie kleur+lijntje opnemen in tabel (zoals die ind e legeda staat)    
    Add pijl voor periode 12 tussen begroot en realisatie en zet text +xx keur of -yy keur (annotate is je vriend)
    realisatie lijn groen als het onder begroot is en rood als het overbegroot is
# fig2:
    remove_pieces: check of er slechts 1 piece verwijdert wordt. Want dan kan je hem beter laten staan!
# fig3: 
    y-labels kleurtje geven (want als niet begroot is, is ie sowieso rood..)

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
        self.resultaat = None #totaal resultaat for whole year
        self.baten = {} #key = ks, np array for each periode (12)
        self.lasten = {} #key = ks, np array for each periode (12)
        self.begroot = {} #key = ks, 1 value for whole year
        pass


    def get_colors(self, valueType, steps):
        if valueType=='lasten':
            return plt.cm.BuPu(np.linspace(0.75, 0.1, steps))

        if valueType=='baten':
            return plt.cm.BuGn(np.linspace(0.75, 0.1, steps))

        sys.exit('unknown color map ' + valueType + ' in Graph.get_colors()') 

    def value_to_table_string(self, value):
        if value == 0 or value < 0.5:
            return ''
        else:
            return ('%.f' % value)

    def realisatie(self, params):
        baten = self.baten.copy()
        lasten = self.lasten.copy()
        resultaat = self.resultaat
        begroting = np.cumsum(self.begroot['totaal'])
        X = np.arange(1,13)
        resultaat = np.cumsum(resultaat)

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

        colorslasten = self.get_colors('lasten', len(lasten))
        colorsbaten = self.get_colors('baten', len(baten))
        colors = np.concatenate( (colorslasten,colorsbaten), axis=0)

        #Plot data
        p1 = plt.plot(X, resultaat, 'ro-', lw=2)
        p2 = plt.plot([0,12], [0,begroting], 'k--')
        legend['data'].append(p1[0])
        legend['keys'].append("Realisatie")
        legend['data'].append(p2[0])
        legend['keys'].append("Begroting")

        if params['show_prognose']:
            z = np.polyfit(X, resultaat, 1)
            p = np.poly1d(z)
            p3 = plt.plot([0,12], p([0,12]))
            legend['data'].append(p3[0])
            legend['keys'].append("Prognose")

        if params['show_details_flat']:
            totaalbars = len(baten)+len(lasten) 
            width= 1./(totaalbars+1)
            offset = (1-totaalbars*width)/2
            i = 0
            for name, Y in lasten.iteritems():
                if params['show_cumsum']:
                    Y = np.cumsum(Y)
                p4 = plt.bar(X+width*i-0.5+offset, Y,  width, color=colors[i])
                i += 1
                #legend['data'].append(p4[0])
                #legend['keys'].append(name)

            for name, Y in baten.iteritems():
                if params['show_cumsum']:
                    Y = np.cumsum(Y)

                p4 = plt.bar(X+width*i-0.5+offset, Y,  width, color=colors[i])
                i += 1
                #legend['data'].append(p4[0])
                #legend['keys'].append(name)

        if params['show_details_stack']:
            width= .36
            offset = (.36)/2
            y_offset_neg = 0
            y_offset_pos = 0
            i = 0
            for name, Y in lasten.iteritems():
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

            y_offset_neg = 0
            y_offset_pos = 0
            for name, Y in baten.iteritems():
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
                text.append(self.value_to_table_string(value))
            cell_text.append(text)
            for key, line in lasten.iteritems():
                text = []
                for value in line:
                    text.append(self.value_to_table_string(value))

                cell_text.append(text)

            for key, line in baten.iteritems():
                text = []
                for value in line:
                    text.append(self.value_to_table_string(value))

                cell_text.append(text)

            columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
            rows = []
            rows.extend(["Realisatie"])
            rows.extend(lasten.keys())
            rows.extend(baten.keys())
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

        #place upper left or lower left (depending on resultaat + or -)
        if resultaat[-1] <0:
            plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
        else:
            plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)

        return plt

    #remove pieces < threshold of the total:
    def remove_small_pieces(self, values, labels):
        rest = 0
        th = 0.15
        totaal = np.sum(values)
        tmpvalues = []
        tmplabels = []
        for i, value in enumerate(values):
            if value/totaal < th:
                rest += value
            else:
                tmpvalues.append(value)
                tmplabels.append(labels[i])

        if rest >0:
            tmpvalues.append(rest)
            tmplabels.append('Overig')

        return tmpvalues, tmplabels

    def baten_lasten_pie(self):
        baten = self.baten.copy()
        lasten = self.lasten.copy()

        # The slices will be ordered and plotted counter-clockwise.
        baten_labels = []
        baten_values = []
        lasten_labels = []
        lasten_values = []

        for key, line in baten.iteritems():
            value = np.sum(line)
            baten_values.append(np.absolute(value))
            baten_labels.append(key + '\n' + str(int(value)) + 'k eur')

        for key, line in lasten.iteritems():
            value = np.sum(line)
            lasten_values.append(value)
            lasten_labels.append(key + '\n' + str(int(value)) + 'k eur')

        lasten_values, lasten_labels = self.remove_small_pieces(lasten_values, lasten_labels)
        baten_values, baten_labels = self.remove_small_pieces(baten_values, baten_labels)

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
        baten = self.baten.copy()
        lasten = self.lasten.copy()
        begroot = self.begroot.copy()

        #data crunching
        names = []
        if lasten:
            names.extend(list(lasten.keys()))
        if baten:
            names.extend(list(baten.keys()))
        realisatie = []
        residu = []
        color_res = []
        X_max = 0
        #Parse all lasten
        for key, line in lasten.iteritems():
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

        #Parse all lasten
        for key, line in baten.iteritems():
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
            if key not in baten and key not in lasten and key != 'totaal':
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
        colorslasten = self.get_colors('lasten', len(lasten))
        colorsbaten = self.get_colors('baten', len(lasten))
        colors = np.concatenate( (colorslasten,colorsbaten), axis=0)

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

    def parse_node(self, root, details, lines, begroot, periode):

        pars = []
        if details:
            pars = root.get_end_children(pars)
        else:
            pars = root.children

        # parse each node
        for node in pars:
            totaal = ( ((node.totaalGeboektTree + node.totaalObligosTree)))
            if periode == 1:
                begroot[node.descr] = node.totaalPlanTree
                lines[node.descr] = [ totaal ]
            else:
                lines[node.descr].append(totaal)

        return lines, begroot

    def to_np_keuro(self, dictionary):
        # Convert to a proper numpy array in keuro.
        for key, line in dictionary.iteritems():
            dictionary[key] = np.array(dictionary[key])/1000

        return dictionary

    def load_order(self, jaar, order, params):
        # Get params
        KSgroep = 1
        maxdepth = 1

        KSgroepen = model.loadKSgroepen()
        grootboekBaten =  [s for s in KSgroepen if "BFRE15BT00" in s][0]
        grootboekLasten = [s for s in KSgroepen if "BFRE15LT00" in s][0]
        sapdatum = config['lastSAPexport']

        begroot = {}
        baten = {}
        lasten = {}

        resultaat = []
        for periode in range(1,13):
            if periode == 12:
                periode == [12,13,14,15]
            rootBaten = GrootBoek.load(order, grootboekBaten, jaar, [periode])
            rootLasten = GrootBoek.load(order, grootboekLasten, jaar, [periode])

            totaal = rootBaten.totaalGeboektTree + rootBaten.totaalObligosTree  
            totaal += rootLasten.totaalGeboektTree + rootLasten.totaalObligosTree  
            resultaat.append(totaal)

            begroot['totaal'] = rootLasten.totaalPlanTree
            begroot['totaal'] += rootBaten.totaalPlanTree

            details = params['detailed']
            baten, begroot = self.parse_node(rootBaten, details, baten, begroot, periode)
            lasten, begroot = self.parse_node(rootLasten, details, lasten, begroot, periode)

        #Remove lines that only have 0's (don't check the sum, could be +50, -50)
#TODO refactor this into a function (double code, and will be tripple code with baten/lasten split)
        remove = []
        for key, line in baten.iteritems():
            if all(v < 500 for v in line):
                remove.append(key)

        for key in remove:
            del baten[key]

        remove = []
        for key, line in lasten.iteritems():
            if all(v < 500 for v in line):
                remove.append(key)

        for key in remove:
            del lasten[key]


        # remove 0 lines that are not in lines (and also dont remove total)
        remove = []
        for key, value in begroot.iteritems():
            if value == 0 and key not in baten and key not in lasten and key!='totaal':
                remove.append(key)

        for key in remove:
            del begroot[key]

        self.begroot = self.to_np_keuro(begroot)
        self.baten = self.to_np_keuro(baten)
        self.lasten = self.to_np_keuro(lasten)
        self.resultaat = np.array(resultaat)/1000

        if not self.baten and not self.lasten:
            return False
        return True


def create_graphs_order(order, jaar, params):
    graph = Graph()
    if graph.load_order(jaar, order, params):
        plt = graph.realisatie(params)
        plt.savefig('figs/'+str(order)+'-1.png', bbox_inches='tight')
        plt.close()

        plt = graph.baten_lasten_pie()
        plt.savefig('figs/'+str(order)+'-2.png', bbox_inches='tight')
        plt.close()

        plt = graph.besteed_begroot()
        plt.savefig('figs/'+str(order)+'-3.png', bbox_inches='tight')
        plt.close()

def create_ordergroep_graphs(OG, jaar, params):
    root = GrootBoekGroep.load(OG)
    #for child in root.children:
        #print child.name

    #test loading of two orders
    order = 2008000000
    graph = Graph()
    if graph.load_order(jaar, order, params):
        plt = graph.realisatie(params)
        plt.savefig('test.png', bbox_inches='tight')
        plt.close()
    if graph.load_order(jaar, order, params):
        plt = graph.realisatie(params)
        plt.savefig('test2.png', bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    params = {}
    params['show_prognose'] = False
    params['show_cumsum'] = False
    params['show_details_flat'] = True
    params['show_details_stack'] = False
    params['show_table'] = True
    params['detailed'] = True

    found = False
    if len(sys.argv) <2:
        print 'error no arguments given'
        print 'use graph.py <order/group>'
        print '* for all orders'

    elif sys.argv[1] == '*':
        found = True
        print 'creating graphs of all orders'
        orders = model.get_orders()
        for i, order in enumerate(orders):
            print '%i (%i out of %i - %i perc.)' % (order, i+1, len(orders), (float(i+1)/len(orders))*100)
            create_graphs_order(order, 2015, params)
    else:
        order = sys.argv[1]
        orders = model.get_orders()
        try:
            orderint = int(order)
        except ValueError:
            orderint = 0
        OGs = model.loadOrdergroepen()

        if orderint in orders:
            found = True
            print 'creating graph of order ' + order
            create_graphs_order(order, 2015, params)
        else:
            for OG in OGs:
                if order == os.path.split(OG)[1]:
                    found = True
                    print 'creating graph of group ' + order
                    create_ordergroep_graphs(OG, 2015, params)


    if not found:
        print 'ERROR Unkown input ' + order
    else:
        print 'great succes!'


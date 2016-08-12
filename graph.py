""""
Usage
    $ python graph.py <order/group>
    use * for all orders

NOTES

    only shows >|500| euro in table

TODO

# Bij het maken van een enkele graph de naam van de order uit een config tabel halen (bestaat nog niet!)
# Kijken naar de if/else structuur van de argv parser. Als je geen argumenten geeft krijg je fout melding .
# Afronding: alleen doen bij visualisatie, niet in export naar files en totalen niet optellen uit afgeronde cijfers.
# Algemeen
    Jaaroverzicht maken -> per jaar doorlinken naar de onderstaande rapportages.
    Hash alle plaatjes met username om te voorkomen dat je ze zo van elkaar kan zien
    Als ordergroep geen groepen eronder heeft gaat het mis. (dus b.v. 2008A3 zo uitdraaien)
# Allow the script to accept 'year' as an input param so we can build any year as well
# Store figs in the proper directory 'static/xxx'
# fig1:

# fig2:
    remove_pieces: check of er slechts 1 piece verwijdert wordt. Want dan kan je hem beter laten staan!
    Als het totaal 0 is moet je toch een pie chart maken met 1 piecie.
# fig3:
    y-labels kleurtje geven (want als niet begroot is, is ie sowieso rood..)

"""
import web
web.config.debug = False #must be done before the rest.

import model
import GrootBoek
import OrderGroep
import os
from config import config
from functions import moneyfmt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pylab as pylab
import sys
from matplotlib.patches import Rectangle



class Graph:
    def __init__(self):
        self.title = ''
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
        if value == 0 or np.abs(value) < 0.5:
            return ''
        else:
            return ('%.f' % value)

    def realisatie(self, params, name_fig):
        baten = self.baten.copy()
        lasten = self.lasten.copy()
        resultaat = self.resultaat
        begroting = np.cumsum(self.begroot['totaal'])
        X = np.arange(1,13)
        resultaat = np.cumsum(resultaat)

        #Layout figure
        plt.figure(figsize=(12, 9))
        plt.title(self.title, loc='right', fontsize=12)

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

        #legend['data'].append(0)
        #legend['keys'].append("Realisatie")

        colorslasten = self.get_colors('lasten', len(lasten))
        colorsbaten = self.get_colors('baten', len(baten))
        colors = np.concatenate( (colorslasten,colorsbaten), axis=0)

        #Plot data
        p1 = plt.plot(X, resultaat, 'ro-', lw=2)
        p2 = plt.plot([0,12], [0,begroting], 'k--')
        legend['data'].append(p1[0])
        legend['keys'].append("Realisatie (" +self.value_to_table_string(resultaat[-1])  + "k)")
        legend['data'].append(p2[0])
        legend['keys'].append("Begroting (" +self.value_to_table_string(begroting[0])  + "k)")
        legend['data'].append(Rectangle( (0,0),0,0, alpha=0.0))
        overschot = begroting[0] - resultaat[-1]
        if overschot>0:
            legend['keys'].append("Te besteden (" + self.value_to_table_string(overschot) + "k)")
        else:
            legend['keys'].append("Overbesteed: (" + self.value_to_table_string(overschot) + "k)")

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
            cell_vals = []
            vals = []
            #Realisatie, begroting en R-B:
            for value in resultaat:
                text.append(self.value_to_table_string(value))
                vals.append(value)
            cell_text.append(text)
            cell_vals.append(vals)
            text = []

            for key, line in lasten.iteritems():
                vals = []
                text = []
                total = 0
                for value in line:
                    if params['show_table_cumsum']:
                        total = total + value
                    else:
                        total = value
                    text.append(self.value_to_table_string(total))
                    vals.append(total)

                cell_text.append(text)
                cell_vals.append(vals)

            for key, line in baten.iteritems():
                vals = []
                text = []
                total = 0
                for value in line:
                    if params['show_table_cumsum']:
                        total = total + value
                    else:
                        total = value
                    text.append(self.value_to_table_string(total))
                    vals.append(total)

                cell_text.append(text)
                cell_vals.append(vals)

            columns = (["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
            rows = []
            rows.extend(["Totaal"])
            rows.extend(lasten.keys())
            rows.extend(baten.keys())
            colors = np.insert(colors, 0, [1,1,1,1], 0) #Hack for making sure color realisatie
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

        #Save data to text
        self.save_to_file(rows, cell_vals, name_fig, columns)

        #place upper left or lower left (depending on resultaat + or -)
        if resultaat[-1] <0:
            leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
        else:
            leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
        leg.get_frame().set_linewidth(0.0)

        return plt

    # Saves the table from exploitatie overview to a text file
    def save_to_file(self, number_descr, numbers, file_name, header_rows):
        datPath = config['graphPath'] + '%s/%s/' % (params['jaar'], 'realisatie')
        if not os.path.isdir(datPath):
            os.makedirs(datPath)

        #table numbers
        header_rows = ','.join(header_rows)
        np.savetxt(datPath + file_name+ '-num.dat', numbers, fmt='%f', header=header_rows)
        #Table hedaers
        import csv
        myfile = open(datPath + file_name+'-descr.dat', 'wb')
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for descr in enumerate(number_descr):
            wr.writerow(descr)

        #Begroting numbers:
        writer = csv.writer(open(datPath+file_name+'-begroot.dat', 'wb'))
        for key, value in self.begroot.items():
            writer.writerow([key, value])

    #remove pieces < threshold of the total:
    def remove_small_pieces(self, values, labels):
        totaal = np.sum(values)
        if totaal == 0:
            return values, labels

        rest = 0
        th = 0.15
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
#TODO fix pie charts als ze uit 0 euro bestaan of uit 1 post.
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
        plt.title(self.title, loc='right', fontsize=12)
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
                X_max = float(max(X_max, (besteed)))
            else:
                color_res.append('lightsage')
                X_max = float(max(X_max, (res+besteed)))
            residu.append(res)

        #Parse all baten
        for key, line in baten.iteritems():
            besteed = np.absolute(np.sum(line))
            realisatie.append(besteed)
            res = np.absolute(begroot[key]) - besteed

            if res <= 0 :
                color_res.append('pink')#pink
                X_max = float(max(X_max, (besteed)))
            else:
                color_res.append('lightsage')
                X_max = float(max(X_max, (res+besteed)))
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
                    X_max = float(max(X_max, (besteed)))
                else:
                    color_res.append('lightsage')
                    X_max = float(max(X_max, (res+besteed)))
                residu.append(res)
                names.append(key) #of gebruik insert(pos, key)

        #Layout figure
        fig, ax = plt.subplots(figsize=(12, 9))
        plt.title(self.title, loc='right', fontsize=12)

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
                xloc = 0.5*width + float(realisatie[i])
                rankStr = '+'+str(width)
            else:
                xloc = -0.4*width + float(realisatie[i])
                rankStr = '-'+str(width)

            xloc = min(xloc, X_max*1.01)
            yloc = rect.get_y()+rect.get_height()/2.0

            ax.text(xloc, yloc, rankStr,
                    verticalalignment='center', color='black', weight='bold')
            i +=1

        return plt


    def to_np_keuro(self, dictionary):
        # Convert to a proper numpy array in keuro.
        for key, line in dictionary.iteritems():
            dictionary[key] = np.array(dictionary[key])/1000

        return dictionary

    def load_order(self, order, params):
        sapdatum = model.last_update()

        resultaat = []
        begroot = {}
        baten = {}
        lasten = {}

        regels = model.get_regellist_per_table(['geboekt', 'obligo', 'plan'], jaar=[params['jaar']], orders=[order])
        root = GrootBoek.load('BFRE15')
        root.assign_regels_recursive(regels)
        root.set_totals()

        rootBaten = root.find("BFRE15BT00")
        rootLasten = root.find("BFRE15BT00")
        rootBaten.clean_empty_nodes()
        rootLasten.clean_empty_nodes()

        for periode in range(1,13):
            if periode == 1:
                begroot['totaal'] = 0

            if periode == 12:
                periode = [12,13,14,15]
            else:
                periode = [periode]

            totalTreeBaten  =  rootBaten.set_totals(periodeRequested=periode)
            totalTreeLasten = rootLasten.set_totals(periodeRequested=periode)

            if params['ignore_obligos']:
                totaal = totalTreeBaten['geboekt'] + totalTreeLasten['geboekt']
            else:
                totaal = totalTreeBaten['geboekt'] + totalTreeLasten['geboekt']
                totaal += totalTreeBaten['obligo'] + totalTreeLasten['obligo']
            resultaat.append(totaal)

            begroot['totaal'] += totalTreeBaten['plan'] + totalTreeLasten['plan']

            details = params['detailed']
            baten, begroot = self.parse_node(rootBaten, details, baten, begroot, periode)
            lasten, begroot = self.parse_node(rootLasten, details, lasten, begroot, periode)

        #Remove lines that only have 0's (don't check the sum, could be +50, -50)
        remove = []
        for key, line in baten.iteritems():
            if all(np.abs(v) < 500 for v in line):
                remove.append(key)

        for key in remove:
            del baten[key]


        remove = []
        for key, line in lasten.iteritems():
            if all(np.abs(v) < 500 for v in line):
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


    def parse_node(self, root, details, lines, begroot, periode):
        pars = []
        if details:
            pars = root.get_end_children(pars)
        else:
            pars = root.children

        # parse each node
        for node in pars:
            if params['ignore_obligos']:
                totaal = node.totaalTree['geboekt']
            else:
                totaal = node.totaalTree['geboekt'] + node.totaalTree['obligo']
            if periode == [1]:
                begroot[node.descr] = node.totaalTree['plan']
                lines[node.descr] = [ totaal ]
            else:
                lines[node.descr].append(totaal)

        return lines, begroot


    #Merges two graphs
    def merge(self, graph):
        if self.resultaat is None:
            self.resultaat = graph.resultaat
        elif sum(self.resultaat) == 0 :
            self.resultaat = graph.resultaat
        else:
            self.resultaat += graph.resultaat

        for key, value in graph.begroot.iteritems():
            if key in self.begroot:
                self.begroot[key] += value
            else:
                self.begroot[key] = value

        for key, arr in graph.baten.iteritems():
            if key in self.baten:
                self.baten[key] = self.baten[key] + arr
            else:
                self.baten[key] = arr

        for key, arr in graph.lasten.iteritems():
            if key in self.lasten:
                self.lasten[key] = self.lasten[key] + arr
            else:
                self.lasten[key] = arr

    def bfr(self):
        return plt_baten, plt_lasten_pl, plt_lasten_ml


    def save_fig(self, plt, params, tiepe, name):
        graphPath = config['graphPath'] + '%s/%s/' % (params['jaar'], tiepe)
        if not os.path.isdir(graphPath):
            os.makedirs(graphPath)
        plt.savefig(graphPath + '%s.png' % str(name), bbox_inches='tight')


    def create_figs(self, name, params):
        plt = self.realisatie(params, name)
        self.save_fig(plt, params, 'realisatie', name)
        plt.close()

        plt = self.baten_lasten_pie()
        self.save_fig(plt, params, 'pie', name)
        plt.close()

        plt = self.besteed_begroot()
        self.save_fig(plt, params, 'bars', name)
        plt.close()


def og_graphs(root, i, total, jaar):
    merged = Graph()
    # Ook alle childs mergen!
    for child in root.children:
        graph, i = og_graphs(child, i, total, jaar)
        merged.merge(graph)

    graph = Graph()
    for order, descr in root.orders.iteritems():
        print '%i (%i out of %i - %i perc.)' % (order, i+1, total, (float(i+1)/total)*100)
        graph.load_order(order, params)
        graph.title = str(order) + ' - ' + descr
        graph.create_figs(str(order), params)
        merged.merge(graph)
        i += 1


    merged.title = root.name + ' - ' + root.descr
    merged.create_figs(root.name, params)

    return merged, i

def create_ordergroep_graphs(OG, params):
    root = OrderGroep.load(OG)

    merged = Graph()
    graph = Graph()
    i = 0
    total = len(root.list_orders_recursive())
    for child in root.children:
        graph, i = og_graphs(child, i, total, params['jaar'])
        merged.merge(graph)

    merged.title = root.name + ' - ' + root.descr
    merged.create_figs(root.name, params)

if __name__ == "__main__":
    params = {}
    params['show_prognose'] = False
    params['show_cumsum'] = False
    params['show_details_flat'] = True
    params['show_details_stack'] = False
    params['show_table'] = True
    params['show_table_cumsum'] = False
    params['detailed'] = True
    params['ignore_obligos'] = False

    found = False
    if len(sys.argv) <2:
        print 'error no arguments given'
        print 'use graph.py <order/group> <jaar>'
        print '* for all orders'

    try:
        target  = sys.argv[1]
    except:
        pass

    year = config["currentYear"] 
    try:
        year = sys.argv[2]
    except:
        pass

    orders_available = model.get_orders()
    years = model.get_years_available()
    if target == '*':
        found = True
        print 'creating graphs of all orders'
        orders = model.get_orders()
        graph = Graph()
        if year == '*':
            for year in years:
                print 'building year %s' % year
                params['jaar'] =year
                for i, order in enumerate(orders):
                    print '%i (%i out of %i - %i perc.)' % (order, i+1, len(orders), (float(i+1)/len(orders))*100)
                    graph.load_order(order, params)
                    graph.title = str(order)
                    graph.create_figs(str(order), params)
        else:
            params['jaar'] = year
            print 'building year %s' % year
            for i, order in enumerate(orders):
                print '%i (%i out of %i - %i perc.)' % (order, i+1, len(orders), (float(i+1)/len(orders))*100)
                graph.load_order(order, params)
                graph.title = str(order)
                graph.create_figs(str(order), params)
    try:
        targetInt = int(target)
    except:
        targetInt = 0
        pass
    if targetInt in orders_available:
        if year == '*':
            for year in years:
                params['jaar'] = year
                found = True
                graph = Graph()
                print 'creating graph of order %s in year %s' %(targetInt, year)
                graph.load_order(targetInt, params)
                graph.title = str(targetInt) + ' - <UNKNOWN>'
                graph.create_figs(str(targetInt), params)
        else:
            params['jaar'] = year
            found = True
            graph = Graph()
            print 'creating graph of order %s in year %s' %(targetInt, year)
            graph.load_order(targetInt, params)
            graph.title = str(targetInt) + ' - <UNKNOWN>'
            graph.create_figs(str(targetInt), params)
    else:
        groepen = model.loadOrderGroepen()
        if target in groepen:
            if year == '*':
                for year in years:
                    params['jaar'] = year
                    found = True
                    print 'creating graph of group %s in year %s' % (target, year)
                    create_ordergroep_graphs(target, params)
            else:
                params['jaar'] = year
                found = True
                print 'creating graph of group %s in year %s' % (target, year)
                create_ordergroep_graphs(target, params)

    if not found:
        print 'ERROR Unkown input ' + target
    else:
        print 'great succes!'

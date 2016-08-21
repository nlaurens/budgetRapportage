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

#overview: 1 kolom extra in elke tabel en daarin het grafiekje van de jaren zetten zodat het goed te zien is
# grafiek: x = jan/dec, y = 0 tot 100% realisatie t.o.v. begroting (dus 1 lijn begroting stippel de rest in kleurtjes
# met in legenda eronder de absolute getallen in realisatie

"""
import web
web.config.debug = False #must be done before the rest.

import model.regels
import model.ordergroup

import os
from config import config
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pylab as pylab
import sys
from matplotlib.patches import Rectangle


def save_fig(plt, year, tiepe, name):
    graphPath = config['graphPath'] + '%s/%s/' % (year, tiepe)
    if not os.path.isdir(graphPath):
        os.makedirs(graphPath)
    plt.savefig(graphPath + '%s.png' % str(name), bbox_inches='tight')


def value_to_table_string(value):
    if value == 0 or np.abs(value) < 0.5:
        return ''
    else:
        return ('%.f' % value)


def construct_data_orders(years, regels, orders):
    data = {}
    return data


def construct_data_groups(years, data_orders, orders):
    data = {}
    return data


def get_colors(steps):
    colors_lasten = plt.cm.BuPu(np.linspace(0.75, 0.1, steps['lasten']))
    colors_baten = plt.cm.BuGn(np.linspace(0.75, 0.1, steps['baten']))
    return np.concatenate((colors_lasten, colors_baten), axis=0)

def graph_realisatie(title_plot, data):
    # DUMMY
    begroting = 100 # np.cumsum(self.begroot['totaal'])
    data_y_resultaat = np.arange(10,22)
    lasten = {'lasten1':np.array([1,1,1,1,1,1,1,1,1,1,1,1])}
    baten = {'baten1': np.array([2,2,2,2,2,2,2,2,2,2,2,2])}

    # setup data
    data_x = np.arange(1,13)
    data_x_begroting = np.array([1, 12])
    data_y_begroting = np.array([0, begroting])
    #data_y_baten = baten
    #data_y_lasten = lasten
    #data_y_resultaat = resultaat

    # Layout figure
    plt.figure(figsize=(12, 9))
    plt.title(title_plot, loc='right', fontsize=12)

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

    colors = get_colors({'lasten':len(lasten), 'baten':len(baten)})
    #TODO

    #Plot data
    plot_resultaat = plt.plot(data_x, data_y_resultaat, 'ro-', lw=2) 
    plot_begroting = plt.plot(data_x_begroting, data_y_begroting, 'k--')
    
    # setup legend
#TODO moneyfmt values in legend
    legend['data'].append(plot_resultaat[0])
    legend['keys'].append("Realisatie (%s keur)" % data_y_resultaat[-1])
    legend['data'].append(plot_begroting[0])
    legend['keys'].append("Begroting (%s keur)" % data_y_begroting[1])
    legend['data'].append(Rectangle( (0,0),0,0, alpha=0.0))
    overschot = begroting - data_y_resultaat[-1]
    if overschot>0:
        legend['keys'].append("Te besteden (%s keur)" % overschot)
    else:
        legend['keys'].append("Overbesteed: (%s keur)" % overschot)

    # place legend in upper left or lower left
    leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=2)
    if data_y_resultaat[-1] < 0:
        leg = plt.legend(tuple(legend['data']), tuple(legend['keys']), fontsize=16, loc=3)
    leg.get_frame().set_linewidth(0.0)

    # Plot bars of baten/lasten!
    totaalbars = len(baten)+len(lasten)
    width= 1./(totaalbars+1)
    offset = (1-totaalbars*width)/2
    bar_nr = 0
    for name, Y in lasten.iteritems():
        plot_lasten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, Y,  width, color=colors[bar_nr])
        bar_nr += 1

    for name, Y in baten.iteritems():
        plot_baten_bars = plt.bar(data_x+width*bar_nr-0.5+offset, Y,  width, color=colors[bar_nr])
        bar_nr += 1

    # add table below the graph
    if False:
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

    return plt

def build_graphs(years):
    # load data
    orders = [2008502040] # orders = model.regels.orders() TODO remove dummy orders
    groups = model.ordergroup.available()
    regels = model.regels.load(years_load=years, orders_load=orders)
    data_orders = construct_data_orders(years, regels, orders)  # load all orders in regels
    data_groups = construct_data_groups(years, data_orders, groups)  # loads all ordergroups

    print data_orders
    print data_groups

    # build graphs
    for order in orders:
        #build_overview(order, data_orders)
        for year in years:
            data = {} # TODO select data for the graph
            title = 'DUMMY POLOT TITLE'  # TODO plot title
            plt = graph_realisatie(title, data)
            #TODO:
            print 'saving fig'
            save_fig(plt, year, 'realisatie', order)
            plt.close()

            exit()

    #for group in groups:
    #    build_overview(group, data_groups)
    #    for year in years:
    #        graph_realisatie(group, data_groups)


if __name__ == "__main__":
    # todo: move to graph 'realisatie' 'overview' class
    #params = {}
    #params['show_prognose'] = False
    #params['show_cumsum'] = False
    #params['show_details_flat'] = True
    #params['show_details_stack'] = False
    #params['show_table'] = True
    #params['show_table_cumsum'] = False
    #params['detailed'] = True
    #params['ignore_obligos'] = False

    # Run it: $python server.py <year>/*
    valid_input = False
    if len(sys.argv) == 2:
        years_available = model.regels.years()
        year = sys.argv[1] 
        if year == '*':
            years = years_available
            valid_input = True
        else:
            if year in years_available:
                years = [year]
                valid_input = True

    if valid_input:
        build_graphs(years)
    else: 
        print 'error in arguments'
        print 'use graph.py <jaar>'
        print '* for all years'

from config import config
import OrderGroep
import GrootBoek
import model
import os
import numpy as np
from functions import moneyfmt
from RegelList import RegelList

def fill_dropdowns(form, settings, KSgroepen):
    dropdownlist = []
    for i, path in enumerate(KSgroepen):
        dropdownlist.append( (i, os.path.split(path)[-1] ))
    form.ksgroep.args = dropdownlist

    form.ksgroep.value = settings["KSgroep"]
    form.jaar.value = settings["jaar"]
    form.maxdepth.value = settings["maxdepth"]
    form.periode.value = settings["periode"]
    form.clean.checked = settings["clean"]

def view(settings, render, form, order):

    KSgroepen = model.loadKSgroepen()
    fill_dropdowns(form, settings, KSgroepen)

    order = int(order)
    sapdatum = model.last_update()

    regels = model.get_regellist_per_table(jaar=[settings["jaar"]], orders=[order])
#TODO replace with param
    root = GrootBoek.load('WNMODEL4')

    root.assign_regels_recursive(regels)
    if settings["clean"]:
        root.clean_empty_nodes()

    root.set_totals()
#TODO replace with param
    rootBaten = root.find('WNTBA')
    rootLasten = root.find('WNTL')

    totaal = {}
    totaal['order'] = order
    totaal['begroting'] = root.totaalTree['plan']
    totaal['baten'] = rootBaten.totaalTree['geboekt'] + rootBaten.totaalTree['obligo']
    totaal['lasten'] = rootLasten.totaalTree['geboekt'] + rootLasten.totaalTree['obligo']

    reserves = model.get_reserves()
    try:
        totaal['reserve'] = reserves[str(order)]
    except:
        totaal['reserve'] = 0

    if totaal['reserve'] < 0:
        totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting'] + totaal['reserve']
    else:
        totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting']

    totaal['reserve'] = moneyfmt(totaal['reserve'])
    totaal['ruimte'] = moneyfmt(totaal['ruimte'])
    totaal['baten'] = moneyfmt(totaal['baten'])
    totaal['lasten'] = moneyfmt(totaal['lasten'])
    totaal['begroting'] = moneyfmt(totaal['begroting'])

    htmlgrootboek = []
    for child in root.children:
        htmlgrootboek.append(html_tree(child, render, settings["maxdepth"], 0))

    return render.webvieworder(form, sapdatum, htmlgrootboek, totaal)


def html_tree(root, render, maxdepth, depth):
    depth += 1

    groups = []
    for child in root.children:
        groups.append(html_tree(child, render, maxdepth, depth))

    unfolded = False # Never show the details

    regelshtml = []
    totalsNode = {} #Always initialize all to 0 to prevent render problems
    totalsNode['geboekt'] = 0
    totalsNode['obligo'] = 0
    totalsNode['plan'] = 0
    for tiepe, regelsPerTiepe in root.regels.iteritems():
        totalsKS = {} #Always initialize all to 0 to prevent render problems
        totalsKS['geboekt'] = 0
        totalsKS['obligo'] = 0
        totalsKS['plan'] = 0
        for ks, regelsPerKS in regelsPerTiepe.split_by_regel_attributes(['kostensoort']).iteritems():
            totalsKS[tiepe] = regelsPerKS.total()
            if tiepe not in totalsNode:
                totalsNode[tiepe] = regelsPerKS.total()
            else:
                totalsNode[tiepe] += regelsPerKS.total()
            for regel in regelsPerKS.regels:
                regel.kosten = moneyfmt(regel.kosten, places=2, dp='.')

                KSname = root.kostenSoorten[ks]
                KSname = str(ks) +' - ' + KSname.decode('ascii', 'replace').encode('utf-8')
                regelshtml.append(render.regels(root.name, ks, KSname, totalsKS, regelsPerKS.regels, unfolded))

    if depth <= maxdepth:
        unfolded = True
    else:
        unfolded = False

    html = render.grootboekgroep(root.name, root.descr, groups, regelshtml, unfolded, totalsNode, depth)

    return html

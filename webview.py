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

    htmlgrootboek = []

    totaal = {}
    totaal['order'] = order
    totaal['baten'] = 0
    totaal['lasten'] = 0
    totaal['ruimte'] = 0

    reserves = model.get_reserves()
    try:
        totaal['reserve'] = reserves[str(order)]
    except:
        totaal['reserve'] = 0

# TODO LOAD BGROTING
    totaal['begroting'] = 0

    if totaal['reserve'] < 0:
        totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting'] + totaal['reserve']
    else:
        totaal['ruimte'] = -1*(root.totaalTree['geboekt'] + root.totaalTree['obligo']) + totaal['begroting']

    for child in root.children:
        htmlgrootboek.append(html_tree(child, render, settings["maxdepth"], 0))

    totaal['reserve'] = moneyfmt(totaal['reserve'])
    totaal['ruimte'] = moneyfmt(totaal['ruimte'])
    totaal['baten'] = moneyfmt(totaal['baten'])
    totaal['lasten'] = moneyfmt(totaal['lasten'])
    totaal['begroting'] = moneyfmt(totaal['begroting'])

# TODO: INFO ERGENS ANDERS VANDAAN HALEN VOOR UL
    #if str(order)[4] != '0' and str(order)[4] != '1':
        #return render.viewproject(grootboek, sapdatum, htmlgrootboek, totaal)

    #print '----------------'
    #root.walk_tree(9999)
    return render.webvieworder(form, sapdatum, htmlgrootboek, totaal)


def html_tree(root, render, maxdepth, depth):
    depth += 1

    groups = []
    for child in root.children:
        groups.append(html_tree(child, render, maxdepth, depth))

    regelshtml = []

    unfolded = False # Never show the details
#regel iteritems zijn nu plannen geen ks! dus per key

    regelsPerKSPerTiepe = RegelList()
    for key, regellist in root.regels.iteritems():
        regelsPerKSPerTiepe.extend(regellist)

    regelsPerKSPerTiepe = regelsPerKSPerTiepe.split_by_regel_attributes(['kostensoort', 'tiepe'])

    totals = {}
    totals['geboekt'] = 0
    totals['obligo'] = 0
    totals['plan'] = 0
    for kostenSoort, regelsPerTiepe in regelsPerKSPerTiepe.iteritems():
        totalsKS = {}
        totalsKS['geboekt'] = 0
        totalsKS['obligo'] = 0
        totalsKS['plan'] = 0
        for tiepe, regellist in regelsPerTiepe.iteritems():
            totalsKS[tiepe] = regellist.total()
            totals[tiepe] += regellist.total()

            for regel in regellist.regels:
                regel.kosten = moneyfmt(regel.kosten, places=2, dp='.')

            KSname = root.kostenSoorten[kostenSoort]
            KSname = str(kostenSoort) +' - ' + KSname.decode('ascii', 'replace').encode('utf-8')
            regelshtml.append(render.regels(root.name, kostenSoort, KSname, totalsKS, regellist.regels, unfolded))

    if depth <= maxdepth:
        unfolded = True
    else:
        unfolded = False

    html = render.grootboekgroep(root.name, root.descr, groups, regelshtml, unfolded, totals, depth)

    return html

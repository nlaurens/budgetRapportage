from config import config
import OrderGroep
import GrootBoek
import model
import os
import numpy as np
from functions import moneyfmt

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

    #root = GrootBoek.load(order, grootboek, settings["jaar"], settings["periode"])
    regels = model.get_regellist_per_table(jaar=[settings["jaar"]], orders=[order])
#TODO replace with param
    root = GrootBoek.load('WNMODEL4')
    root.assign_regels_recursive(regels)
    if settings["clean"]:
        root.clean_empty_nodes()

    root.set_totals()

    totaal = {}
    htmlgrootboek = []

    totaal['order'] = order
    totaal['baten'] = 0
    totaal['lasten'] = 0
    totaal['ruimte'] = 0

#TODO reserves toevoegen
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
        htmlgrootboek.append(child.html_tree(render, settings["maxdepth"], 0))

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
    return render.webvieworder(form, grootboek, sapdatum, htmlgrootboek, totaal)


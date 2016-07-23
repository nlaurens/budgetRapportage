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
    grootboek = KSgroepen[settings["KSgroep"]]
    sapdatum = model.last_update()

    root = GrootBoek.load(order, grootboek, settings["jaar"], settings["periode"])
    if settings["clean"]:
        root.clean_empty_nodes()

#TODO Begroting uit sap 'plan' halen!
    #begroting = model.get_begroting() # dit is de oude functie van VU
    totaal = {}
    htmlgrootboek = []

    totaal['order'] = order
    totaal['baten'] = 0
    totaal['lasten'] = 0
    totaal['ruimte'] = 0

    reserves = model.get_reserves()
    try:
        totaal['reserve'] = reserves[str(order)]
    except:
        totaal['reserve'] = 0


    totaal['begroting'] = 0

    if totaal['reserve'] < 0:
        totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting'] + totaal['reserve']
    else:
        totaal['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree) + totaal['begroting']

    for child in root.children:
        htmlgrootboek.append(child.html_tree(render, settings["maxdepth"], 0))
# TODO: DIT IS SPECIFIEK VOOR 29FALW2
        if child.name == 'BATEN-2900':
            totaal['baten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))
        elif child.name == 'LASTEN2900':
            totaal['lasten'] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))

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


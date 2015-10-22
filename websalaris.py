""""

"""
import web
import model
import GrootBoek
import GrootBoekGroep
from RegelList import RegelList
import os
from config import config
from functions import moneyfmt, IpBlock
from pprint import pprint 

# get regels geboekt
regels = model.get_salaris_geboekt_regels(2015)
regelsGeboekt = RegelList(regels)

# get begroting
regels = model.get_salaris_begroot_regels(2015)
regelsBegroot = RegelList(regels)
begrootDict = regelsBegroot.split_by_regel_attributes(['order', 'personeelsnummer'])

# Cross personeelsnummers begroting -> boekingsnummers
begroot = regelsBegroot.split_by_regel_attributes(['personeelsnummer'])
kosten = regelsGeboekt.split_by_regel_attributes(['personeelsnummer'])

for begrootpersoneelsnummer in begroot.keys():
    begrootpersoneelsnummer = list(begrootpersoneelsnummer.strip())
    if begrootpersoneelsnummer:
        if begrootpersoneelsnummer[0] == '2':
            begrootpersoneelsnummer[0] = '9'
        elif begrootpersoneelsnummer[0] == '1':
            begrootpersoneelsnummer[0] = '8'
        begrootpersoneelsnummer = ''.join(begrootpersoneelsnummer)
        if long(begrootpersoneelsnummer) in kosten.keys():
            print 'ja'
        else:
            print 'nee'
exit()

# dict per order per persnr
kostenDict = regelsGeboekt.split_by_regel_attributes(['order', 'personeelsnummer'])
for order in kostenDict.keys():
    totalOrder = 0
    for personeelsnummer, regelsGeboekt in kostenDict[order].iteritems():
        total = regelsGeboekt.total()
        totalOrder += total
        print 'order %s - persnr %s - kosten %i - begroot TODO (name check: XX - YY)' % (order, personeelsnummer, total)

    print 'order %s - totaal %i' % (order, totalOrder)
    print ''

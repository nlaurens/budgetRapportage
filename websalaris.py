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

def get_begroting_geboekt(userID, groepstr, jaar):
    regels = model.get_salaris_geboekt_regels(jaar)
    regelsGeboekt = RegelList(regels)

    regels = model.get_salaris_begroot_regels(jaar)
    regelsBegroot = RegelList(regels)

    return regelsGeboekt, regelsBegroot

def correlate_personeelsnummers(regelsBegroot, regelsGeboekt):
# Cross personeelsnummers begroting -> boekingsnummers
    begroot = regelsBegroot.split_by_regel_attributes(['personeelsnummer'])
    kosten = regelsGeboekt.split_by_regel_attributes(['personeelsnummer'])

    matchpersoneelsnummers = {} # personeelsnummer in kosten: { regels begroot}
    noMatchPerOrder = {} # order : {regelList met regels}
    for begrootpersoneelsnummer, begrootRegelsList in begroot.iteritems():
        begrootpersoneelsnummer = list(begrootpersoneelsnummer.strip())

        if begrootpersoneelsnummer:
            matchfound = False
            if begrootpersoneelsnummer[0] == '2':
                begrootpersoneelsnummer[0] = '9'
            elif begrootpersoneelsnummer[0] == '1':
                begrootpersoneelsnummer[0] = '8'
            begrootpersoneelsnummer = ''.join(begrootpersoneelsnummer)

            if long(begrootpersoneelsnummer) in kosten.keys():
                matchpersoneelsnummers[long(begrootpersoneelsnummer)] = begrootRegelsList
                matchfound = True

        if not matchfound or not begrootpersoneelsnummer:
            begrootRegelsDictPerOrder = begrootRegelsList.split_by_regel_attributes(['order'])
            for order, begrootRegelsList in begrootRegelsDictPerOrder.iteritems():
                if order not in noMatchPerOrder:
                    noMatchPerOrder[order] = begrootRegelsList
                else:
                    noMatchPerOrder[order].extend(begrootRegelsList)

    return matchpersoneelsnummers, noMatchPerOrder

def groep_report(userID, render, groepstr, jaar):
    report = {}
    regelsGeboekt, regelsBegroot = get_begroting_geboekt(userID, groepstr, jaar)
    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regelsBegroot, regelsGeboekt)

    body = 'TODO BODY'
    settings = 'TODO settings'
    summary = 'TODO summary'
    report['settings'] = settings
    report['summary'] = summary
    report['body'] = body
    return report


def cmd_output(userID, groepstr, jaar):
    regelsGeboekt, regelsBegroot = get_begroting_geboekt(userID, groepstr, jaar)
    matchpersoneelsnummers, noMatchPerOrder = correlate_personeelsnummers(regelsBegroot, regelsGeboekt)


# dict per order per persnr
    kostenDict = regelsGeboekt.split_by_regel_attributes(['order', 'personeelsnummer'])
    totalBegroot = 0
    totalGeboekt = 0
    for order in kostenDict.keys():
        begroot = 0
        totalOrderGeboekt = 0
        totalOrderBegroot = 0
        for personeelsnummer, regelsGeboekt in kostenDict[order].iteritems():
            naamGeboekt = regelsGeboekt.regels[0].personeelsnaam
            geboekt = regelsGeboekt.total()
            totalOrderGeboekt +=  geboekt

            naamBegroot = '' # Reset begroot to not found
            begroot = 0

            if personeelsnummer in matchpersoneelsnummers:
                persoonbegroot = matchpersoneelsnummers[personeelsnummer].split_by_regel_attributes(['order'])
                if order in persoonbegroot:
                    begroot = persoonbegroot[order].total()
                    naamBegroot = persoonbegroot[order].regels[0].personeelsnaam
                    totalOrderBegroot +=  begroot

            print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (order, personeelsnummer, geboekt, begroot, naamGeboekt, naamBegroot)
        
        if order in noMatchPerOrder:
            for regel in noMatchPerOrder[order].regels:
                print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (order, regel.personeelsnummer, 0, regel.kosten, '', regel.personeelsnaam)
                totalOrderBegroot += regel.kosten
            del noMatchPerOrder[order] #Remove so we end up with a list of remaining begrotingsposten

        print 'Total order %s - geboekt %i begroot %i' % (order, totalOrderGeboekt, totalOrderBegroot)
        print ''
        totalBegroot += totalOrderBegroot
        totalGeboekt += totalOrderGeboekt

    print '--------------'
    print 'Begroot maar geen kosten gemaakt op order'
    print ''

    for order, regelList in noMatchPerOrder.iteritems():
        totalOrderBegroot = 0
        for regel in regelList.regels:
            print '  order %s - persnr %s - kosten %i - begroot %i (%s - %s)' % (regel.order, regel.personeelsnummer, 0, regel.kosten, '', regel.personeelsnaam)
            totalOrderBegroot += regel.kosten

        totalBegroot += totalOrderBegroot

        print 'Total order %s - geboekt %i begroot %i' % (order, totalOrderGeboekt, totalOrderBegroot)
        print ''

    print 'TOTAL geboekt %i begroot %i' % (totalGeboekt, totalBegroot)


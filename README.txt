Installation
------------

Requires web.py, mysqldb, iptools

Todo/Bugs
---------
* Maybe one day for wbs: http://jsfiddle.net/jhfrench/GpdgF/

Export SAP posten
-----------------

* Inloggen SAP

* KOBP - Afzonderlijke Planposten 
    * Order-range of -groep selecteren
    * Periode en Boekjaar invullen
    * Overige Layout instellingen - max.aantal treffers > 1M
    * Uitvoeren
    * Geen Aggergatie in layout en minimaal de volgende velden (CTRL+F8)
        * Order
        * Kostensoort
        * Naam v. kostensoort
        * Totaalwrd./vslg.val.
        * Boekjaar
        * (Tip sla layout op als template)
    * Alle kolommen uitrekken totdat gehele header zichtbaar is
    * Exporteer naar Excel XXL-indeling (CTRL+SHFT+F7)
    * In Excel: Sla op als CSV file

* KOB2 - Afzonderlijke obligo
    * Order-range of -groep selecteren
    * Periode invullen
    * 'Alleen open posten' aanvinken
    * Overige Layout instellingen - max.aantal treffers > 1M
    * Uitvoeren
    * Geen Aggergatie in layout en minimaal de volgende velden (CTRL+F8)
        * Order
        * Kostensoort
        * Naam v. kostensoort
        * Waarde/CO-valuta
        * Boekjaar
        * Periode
        * Omschrijving
        * (Tip sla layout op als template)
    * Alle kolommen uitrekken totdat gehele header zichtbaar is
    * Exporteer naar Excel XXL-indeling (CTRL+SHFT+F7)
    * In Excel: Sla op als CSV file

* KOB1 - Afzonderlijke posten
    * Order-range of -groep selecteren
    * Periode invullen
    * Overige Layout instellingen - max.aantal treffers > 1M
    * Uitvoeren
    * Geen Aggergatie in layout en minimaal de volgende velden (CTRL+F8)
        * Order
        * Kostensoort
        * Naam v. kostensoort
        * Waarde/CO-valuta
        * Boekjaar
        * Periode
        * Omschrijving
        * (Tip sla layout op als template)
    * Alle kolommen uitrekken totdat gehele header zichtbaar is
    * Exporteer naar Excel XXL-indeling (CTRL+SHFT+F7)
    * In Excel: Sla op als CSV file


Import SAP posten in MySQL
--------------------------
https://phpmyadmin.vu.nl/

* Open PHP my admin interface
* Browse naar de juiste DB (linker tab)
* Importeren
    * Selecter CSV bestand
    * Vink aan: 'De eerste regel van het bestand bevat kolomnamen (..)'
    * Start

* Hernoem tables naar:
    * plan
    * geboekt
    * obligo

* Verander sap export datum in config.py
    
kostensoortgroep exporeteren/importeren
---------------------------------------

# Vanuit Sap exporteren:
    * Controlling -> Kostensoortgroep -> Weergeven
    * Kostensoortgroep opgeven (b.v. 29FALW2)
      -> Uitvoeren
    * Met de hand alles uitklappen (tip: begin onderaan)
    * Opslaan als bestand (SHFT+F8)
      - kies RAW

# Verwerken voor python:
    * Open bestand in editor (notepad++)
    * Encoding -> Convert to UTF8

Draaien van de server
--------------------

Als tmux sessie al draait:
* Enter tmux attach
* Stop the server (ctrl + c)
* Rotate log
  -> copy server.log -> server.log.x
  -> remove server.log
* Restart server:
  -> $ python server.py 8081 > server.log

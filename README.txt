Installation
------------

* Requires 
  web.py, mysqldb, iptools, xlsx2csv

* Setup config
  Copy config.py.example to config.py and fill out required fields (mysql)

* Setup sap date and load data
  open: http://localhost:8081/admin

Todo/Bugs
---------
* Maybe one day for wbs: http://jsfiddle.net/jhfrench/GpdgF/


Usage
-----

* Start als server

    Als losse service
        -> $ python server.py 8081 

    In TMUX
    * Start/Enter tmux attach
    * Stop the server (ctrl + c)
    * Rotate log
        -> copy server.log -> server.log.x
        -> remove server.log
    * Restart server:
        -> $ python server.py 8081 > server.log


* Webbrowser
    http://localhost:8081/login/<USER HASH>
    http://localhost:8081/salaris/<USER HASH>
    http://localhost:8081/view/<USER HASH>
    http://localhost:8081/report/<USER HASH>
    http://localhost:8081/admin

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

* KOB1 - Werkelijke posten
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

* Y_DEV_55000165 - Geboekte Salarislasten
    * Bedrijfsnummer invullen
    * Kostenplaats range invullen
    * Begin/einddatum
    * Uitvoeren
    * Layout(CTRL + F8) minimaal (geen agregatie!)
        * Personeelsnummer
        * Naam
        * Schaal
        * Trede
        * Kostenplaaats
        * Omschrijving kostenplaaats
        * Kostensoort
        * Omschrijving kostensoort
        * Bedrag
        * Invoerdatum
    * Alle kolommen even breed
    * Exporteer naar Excel: Lijst -> Exporteren -> Spreadsheet -> XXL -> tabel

Import SAP posten in MySQL
--------------------------
http://localhost:8081/admin

XLSX files uploaden.
    
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


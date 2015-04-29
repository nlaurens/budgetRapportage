# Maybe one day for wbs: http://jsfiddle.net/jhfrench/GpdgF/
# SAP rapportage

Export SAP
----------
* Inloggin in SAP

* Onderstaande 2x herhalen: 
  1. Voor kostenplaatsen
  2. Voor ordernummers

* Verslaggroep: Z444
    * Periode van: 1
    * Periode tot: 16
    * Planversie: 1
    * "Meervoudige selectie" knop bij "Of waarde(n)" 
        1.
            * Importeren uit tekstbestand (groene knop onderaan)
            * Selecteer OL-lijst.txt uit directory tool
            * Accepteren
        2. 
            * Range: 2860000 - 2869999
    * Kostensoortgroep: 29FALW2
    * Uitvoeren

* Selecteer posten van "**** Totaal" veld onderin (obligo en werkelijke posten).

* Layout wijzigen (CTRL+F8)
    * Toevoegen:
        * Boekjaar (staat er voor werkelijke kosten al tussen!)
        * Periode
    * Vink Aggregatie uitzetten (als ze aanstaan) bij:
        * Waarde/CO-valuat uitzetten
        * Hoeveelheid totaal
    * Overnemen

* Exporeteren naar Excel (CTR+SHIFT+F7)
    * Uit alle beschik. formaten select
        * Microsoft Excel (2007-xlsx)
    * Akkoord (might take a while)
    * Naam file: 'input.xlsx'

* Andere optie voor tab-sep input:
    * Lokaal bestand
        * Spreadsheet
        * Naam: "input.SAP'

    * Open bestand in notepad++
        * Copy naar new bestand
        * Remove 1st 3 rows and empty 5th row.
        * Save as input.csv
    

Import rapportage in MySQL
--------------------------
https://phpmyadmin.vu.nl/

* Open the excel sheet
    * Save as 'CSV' file

* Open PHP my admin interface
* Browse naar de juiste DB (linker tab)
* Importeren
    * Selecter bestand
    * Vervang comma gescheiden door een puntcomma (';')
    * Vink aan: 'De eerste regel van het bestand bevat kolomnamen (..)'
    * Start*

* Hernoem tables naar:
    * geboekt
    * obligo
    
* Verander type's in de DB!


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

# Maybe one day for wbs: http://jsfiddle.net/jhfrench/GpdgF/
# SAP rapportage

* Inloggin in SAP
* Verslaggroep: Z444
    * Periode van: 1
    * Periode tot: 16
    * "Meervoudige selectie" knop bij "Of waarde(n)" 
        * Importeren uit tekstbestand (groene knop onderaan)
        * Selecteer OL-lijst.txt uit directory tool
        * Accepteren
    * Kostensoortgroep: 28TOTAAl4
    * Uitvoeren

* Selecteer werkelijke posten van "**** Totaal" veld onderin.

* Layout wijzigen
    * Toevoegen:
        * Waarde/TrVal
        * Periode
        * Boekjaar
    * Verwijderen
        * Waarde/CO-valuta
    * Overnemen

* Exporeteren naar Excel
    * Uit alle beschik. formaten select
        * Microsoft Excel (2007-xlsx)
    * Akkoord.
    * Naam file: 'input.xlsx'

Andere optie voor tab-sep input:
* Lokaal bestand
    * Spreadsheet
    * Naam: "input.SAP'

* Open bestand in notepad++
    * Copy naar new bestand
    * Remove 1st 3 rows and empty 5th row.
    * Save as input.csv
    

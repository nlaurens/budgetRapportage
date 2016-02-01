config = {
    "IpRanges": '127.0.0.0 127.255.255.255 10.0.0.1 10.255.255.255',
    "globalPW": '<PASSWORD>',
    "lastSAPexport": '15 Sep 2015',
    "salt": '<UNIQUE SALT>',
    "mysql": {
        "user": "<USER NAME>",
        "pass": "<PASSWORD>",
        "db": "<DB NAME>",
        "host": ""
    },
    "SAPkeys": {
        "types":{
            "order": "int",
            "kostensoort": "int",
            "kostensoortnaam": "varchar(255)",
            "kosten": "decimal(19,4)",
            "jaar": "int",
            "periode": "int",
            "omschrijving": "varchar(255)",
            "documentnummer": "int",
            "invoerdatum": "varchar(255)",
        },
        "geboekt":{
            "order": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "kosten": "Waarde/CO-valuta",
            "jaar": "Boekjaar",
            "periode": "Periode",
            "omschrijving": "Omschrijving",
            "documentnummer": "Documentnummer",
            "invoerdatum": "Invoerdatum",
        },
        "obligo":{
            "order": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "kosten": "Waarde/CO-valuta",
            "jaar": "Boekjaar",
            "periode": "Periode",
            "omschrijving": "Omschrijving",
            "documentnummer": "Nr. referentiedoc.",
        },
        "plan":{
            "order": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "jaar": "Boekjaar",
            "documentnummer": "Documentnummer",
            "kosten": "Totaalwrd./vslg.val.",
        },
        "salaris":{
            "order": "Kostenpl.",
            "ordernaam": "Omschr. Kost.pl.",
            "kostensoort": "Gr.boek",
            "kostensoortnaam": "omschr.g.boekrek.",
            "kosten": "Bedrag",
            "personeelsnummer": "PersNr",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Tr.",
        },
        "salaris_begroting":{
            "order": "Order",
            "kosten": "Kosten",
            "personeelsnummer": "Personeelsnummer",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Trede",
        },
    }
}

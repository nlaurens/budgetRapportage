users = {
    'niels': 'LION.*',
    'test': 'LION.PL',
    'test2': 'LION.PL-TP,PL-BP'
}
config = {
    "IpRanges": '127.0.0.0 127.255.255.255 10.0.0.1 10.255.255.255',
    "globalPW": '...',
    "salt": '...',
    "currentYear": 2016,
    "ksGroupsPath": 'data/ksgroups/',
    "orderGroupsPath": 'data/ordergroups/',
    "graphs":{
        "path": 'graphs/',
        "ksgroup": 'LION',
        "baten": 'LION-B',
        "lasten": 'LION-L',
    },
    "mysql": {
        "user": "...",
        "pass": "...",
        "db": "...",
        "host": "",
        "tables": {
            "config": "config",
            "orderlijst": "orderlijst",
            "regels":{
                "geboekt": "geboekt",
                "obligo": "obligo",
                "plan": "plan",
            },
        },
    },
    "SAPkeys": {
        "types":{
            "ordernummer": "int",
            "kostensoort": "int",
            "kostensoortnaam": "varchar(255)",
            "kosten": "decimal(19,2)",
            "jaar": "int",
            "periode": "int",
            "omschrijving": "varchar(255)",
            "documentnummer": "varchar(255)",
            "invoerdatum": "varchar(255)",
            "personeelsnummer": "int",
            "personeelsnaam": "varchar(255)",
            "schaal": "varchar(255)",
            "trede": "int",
            "ordernaam": "varchar(255)",
            "budgethouder": "varchar(255)",
            "budgethoudervervanger": "varchar(255)",
            "activiteitenhouder": "varchar(255)",
            "activiteitenhoudervervanger": "varchar(255)",
            "activiteitencode": "varchar(255)",
            "subactiviteitencode": "varchar(255)",
        },
        "geboekt":{
            "ordernummer": "Order",
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
            "ordernummer": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "kosten": "Waarde/CO-valuta",
            "jaar": "Boekjaar",
            "periode": "Periode",
            "omschrijving": "Omschrijving",
            "documentnummer": "Nr. referentiedoc.",
        },
        "plan":{
            "ordernummer": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "jaar": "Boekjaar",
            "documentnummer": "Documentnummer",
            "kosten": "Totaalwrd./vslg.val.",
        },
        "salaris_geboekt":{
            "personeelsnummer": "PersNr",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Tr.",
            "ordernummer": "Kostenpl.",
            "ordernaam": "Omschr. Kost.pl.",
            "kostensoort": "Gr.boek",
            "kostensoortnaam": "omschr.g.boekrek.",
            "kosten": "Bedrag",
            "invoerdatum": "Begda afr.",
        },
        "salaris_plan":{
            "personeelsnummer": "Personeelsnummer",
            "personeelsnaam": "Naam",
            "trede": "Trede",
            "ordernummer": "Order",
            "schaal": "Schaal",
            "kosten": "Kosten",
        },
        "orderlijst":{
            "ordernummer": "Order",
            "ordernaam": "Korte tekst",
            "budgethouder": "Naam budgethouder",
            "activiteitenhouder": "Naam acth.",
            "budgethoudervervanger": "Naam vervanger budgeth.",
            "activiteitenhoudervervanger": "Naam vervanger acth.",
            "activiteitencode": "Code",
            "subactiviteitencode": "Sub activiteiten code",
        },
    }
}

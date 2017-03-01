config = {
    "auth":{
        "settings":{
            'url_after_login': '/',
        },
        "tables":[ 
            """
            DROP TABLE IF EXISTS `user`;
            """,
            """
            CREATE TABLE user (
                user_id             int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                user_login          varchar(64) NOT NULL,
                user_password       varchar(255) NOT NULL,
                user_email          varchar(64),  # Optional, see settings
                user_status         varchar(16) NOT NULL DEFAULT 'active',
                user_last_login     datetime NOT NULL DEFAULT '000-00-00'
            )
            """,

            """
            DROP TABLE IF EXISTS `permission`;
            """,
            """
            CREATE TABLE permission (
                permission_id           int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                permission_codename     varchar(50),  # Example: 'can_vote'
                permission_desc         varchar(50)   # Example: 'Can vote in elections'
            )
            """,

            """
            DROP TABLE IF EXISTS `user_permission`;
            """,
            """
            CREATE TABLE user_permission (
                up_user_id          int REFERENCES user (user_id),
                up_permission_id    int REFERENCES permission (permission_id),
                PRIMARY KEY (up_user_id, up_permission_id)
            )
            """
        ],
    },
    "currentYear": 2017,
    "ksGroupsPath": 'data/ksgroups/',
    "orderGroupsPath": 'data/ordergroups/',
    "graphs":{
        "path": 'graphs/',
        "ksgroup": 'KSGROUP',
        "baten": 'KSGROUP-B',
        "lasten": 'KSGROUP-L',
    },
    "mysql": {
        "user": "<USER>",
        "pass": "<PASS>",
        "db": "<DB>",
        "host": "<HOST>",
        "tables": {
            "config": "config",
            "orderlijst": "orderlijst",
            "regels":{
                "geboekt": "posten_geboekt",
                "obligo": "posten_obligo",
                "plan": "posten_plan",
                "salaris_plan": "salaris_plan",
                "salaris_geboekt": "salaris_geboekt",
                "salaris_obligo": "salaris_obligo",
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
            "payrollnummer": "int",
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
            "jaar": "Jaar",
            "ordernummer": "Order",
            "personeelsnummer": "Personeelsnummer",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Trede",
            "kosten": "Kosten",
        },
        "salaris_obligo":{
            "jaar": "Jaar",
            "periode": "Maand",
            "ordernummer": "Kpl",
            "personeelsnummer": "Pernr",
            "payrollnummer": "Payroll",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Tr",
            "kosten": "Tot TB+TSL",
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

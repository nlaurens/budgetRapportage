config = {
    "auth": {
        "settings": {
            'url_after_login': '/',
            'auto_map': False,
        },
        "tables": [
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
    "graphs": {
        "path": 'graphs/',
        "ksgroup": 'LION',
        "baten": 'LION-B',
        "lasten": 'LION-L',
    },
    "mysql": {
        "user": "root",
        "pass": "root",
        "db": "sap",
        "host": "",
        "tables_regels": {
            "geboekt": "posten_geboekt",
            "obligo": "posten_obligo",
            "plan": "posten_plan",
            "salaris_plan": "salaris_plan",
            "salaris_geboekt": "salaris_geboekt",
            "salaris_obligo": "salaris_obligo",
        },
        "tables_other": {
            "user": "user",
            "permission": "permission",
            "user_permission": "user_permission",
            "config": "config",
            "orderlijst": "orderlijst",
        },
    },
    "SAPkeys": {
        "types": {
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
            "activiteitenhouder": "varchar(255)",
            "activiteitencode": "varchar(255)",
            "subactiviteitencode": "varchar(255)",
            "functie": "varchar(255)",
            "geboortedatum": "varchar(255)",
            "contracttiepe": "varchar(255)",
            "contractstart": "varchar(255)",
            "contractstop": "varchar(255)",
            "fte": "decimal(19,2)",

        },
        "geboekt": {
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
        "obligo": {
            "ordernummer": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "kosten": "Waarde/CO-valuta",
            "jaar": "Boekjaar",
            "periode": "Periode",
            "omschrijving": "Omschrijving",
            "documentnummer": "Nr. referentiedoc.",
        },
        "plan": {
            "ordernummer": "Order",
            "kostensoort": "Kostensoort",
            "kostensoortnaam": "Naam v. kostensoort",
            "jaar": "Boekjaar",
            "documentnummer": "Documentnummer",
            "kosten": "Totaalwrd./vslg.val.",
        },
        "salaris_geboekt": {
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
            "jaar": "Jaar",
        },
        "salaris_plan": {
            "jaar": "Jaar",
            "ordernummer": "Order",
            "personeelsnummer": "Personeelsnummer",
            "personeelsnaam": "Naam",
            "schaal": "Schaal",
            "trede": "Trede",
            "kosten": "Kosten",
        },
        "salaris_obligo": {
            "jaar": "Jaar",
            "periode": "Maand",
            "ordernummer": "Kpl",
            "personeelsnummer": "Pernr",
            "payrollnummer": "Payroll",
            "personeelsnaam": "Naam",
            "functie": "Pers cat",
            "contracttiepe": "V/T",
            "schaal": "Schaal",
            "trede": "Tr",
            "geboortedatum": "Geb dat",
            "contractstart": "Begin dvb",
            "contractstop": "Eind dvb",
            "fte": "Fte IT8",
            "kosten": "Tot TB+TSL",
        },
        "orderlijst": {
            "ordernummer": "Order",
            "ordernaam": "Korte tekst",
            "budgethouder": "Naam budgethouder",
            "activiteitenhouder": "Naam acth.",
            "activiteitencode": "Code",
            "subactiviteitencode": "Sub activiteiten code",
        },
    }
}


def init_auth_db(db):
    from auth import auth
    for table in config['auth']['tables']:
        db.query(table)

    auth.create_permission('admin', 'Access to admin panel')
    auth.create_permission('orderlist', 'Access to the orderlist')
    auth.create_permission('salaris', 'Access to the salaris tools')
    auth.create_permission('report', 'Access to the report tools')
    auth.create_permission('view', 'Access to the view tools')

    auth.create_user('admin', password='123admin',
                     perms=['admin', 'orderlist', 'salaris', 'report', 'view', 'orders-all'])

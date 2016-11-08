"""
.ksgroup
    .available() -> list of ksgroups as str
    .load( name as str ) -> KostensoortGroup

.ordergroup
    .available() -> list of ordergroups as str
    .load( name as str ) -> OrderGroup
    .load_sap( path_sap_export_file as str ) -> OrderGroup
        # Note don't use load_sap() for reports/graphs/etc. Only for
        # converting sap exports to txt files that can be used in .load()

.regels
    .exists( tableName as str) -> True/False
    .load(years_load=[], periods_load=[], orders_load=[], table_names_load=[], kostensoort_load=[]) -> RegelList
    .count() -> dict.dict: {<table as str>: <year as int>:<amount of regels as int>}
    .last_update( newdate=<str> ) -> writes/reads last_update as str from/to db
    .years() -> years available in regels db as int - sorted
    .orders() -> orders available in regels db as int
    .kostensoorten() -> kostensoorten available in regels db as int
    .delete(years=[], tableNames=[]) -> total regels deleted from db as int
    .add TODO

.orders
    .TODO

.user
    TODO

"""
__ALL__ = ['ksgroup', 'ordergroup', 'regels', 'orders']

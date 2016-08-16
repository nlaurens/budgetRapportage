""" 
Available functions in model:
    .ksgroup
        .available() -> list of ksgroups as str
        .load( name as str ) -> KostensoortGroup
    .ordergroup
        .available() -> list of ordergroups as str
        .load( name as str ) -> OrderGroup
        .load_sap( path_sap_export_file as str ) -> OrderGroup
            # Note don't use load_sap() for reports/graphs/etc. Only for
            # converting sap exports to txt files that can be used in .load()
    .regellist
    .regels
    .user

-------------
TODO
model.regellist
    .load( year=[], orders=[], tablesNames=[])
        input: year as list of int,
               orders as list of int,
               tablesNames as list of str
        output: dict.value: RegelList instance
                dict.key: tableNames as str

model.regels
    .lastupdate(newdate='')
        input: newdate to be written in the db as str
        output: last sap update from db as a string

    .count()
        input: None
        output: dict.value: number of regels as int,
                dict.key: tableNames as str

    .years(tableNames=[])
        input: tableName as list of str
        output: dict.value: sorted years as list of int,
                dict.key: tableNames as str

    .orders(tableNames=[])
        input: tableName as list of str
        output: dict.value: orders as list of int,
                dict.key: tableNames as str

    .ks(tableNames=[])
        input: tableName as list of str
        output: dict.value: kostensoorten as list of int,
                dict.key: tableNames as str

    .delete(year, tableNames=[])
        input: year als int, tableNames as list of str
        output: total amount of regels deleted as int

    .add(TODO) -> Think on how to load the regels to the db from the xlsx
        input: 
        output:

model.users
    TODO

"""

__ALL__ = ['ksgroup', 'ordergroup']

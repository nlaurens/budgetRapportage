""" 
Available functions in model:

model.ksgroup
    .load( name )
        input: name as str
        returns: instance of KostenSoortGroep

    .available() 
        input: None 
        output: names of kostensoortgroepen as a list of str

model.ordergroup
    .load( name )
        input: name as str
        output: instance of OrderGroep

    .available() 
        input: None 
        output: names of ordergroepen as a list of str

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

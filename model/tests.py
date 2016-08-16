import model.ksgroup
import model.ordergroup
import model.regels

def ksgroups():
    ksgroups = model.ksgroup.available()
    ksgroup = model.ksgroup.load(ksgroups[0])
    print ksgroups
    print ksgroup
    ksgroup.walk_tree(99)

def ordergroups():
    ordergroups = model.ordergroup.available()
    ordergroup = model.ordergroup.load(ordergroups[0])
    print ordergroups
    print ordergroup
    ordergroup.walk_tree(99)

def regels_load():
    regels = model.regels.load()
    regels = regels.split(['tiepe'])
    print regels

def regels_count():
    print model.regels.count()

def sap_update():
    import random
    random_str = random.choice("abcdefgh")
    model.regels.last_update(random_str)
    result = model.regels.last_update()
    print 'Setting db to %s' % random_str
    print 'Result from db: %s' % result
    if result == random_str:
        print 'test succesf'
    else:
        print 'test failed'

def orders():
    print model.regels.orders()

def kostensoorten():
    print model.regels.kostensoorten()

def regels_delete():
    print 'deleting test is not enabled.. manually enable it'
    #print model.regels.delete(years=[2015], tableNames=['plan'])
    #print model.regels.delete()

# Select test
#ksgroups()
#ordergroups()
#regels_load()
#regels_count() #also tests model.regels.years
#sap_update()
#orders()
#kostensoorten()
#regels_delete()

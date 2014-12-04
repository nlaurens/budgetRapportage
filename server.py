# TODO
# grootboek haalt alle kostensoorten die in de grootboek zitten
# op uit de mysql DB. Een hoop kostensoorten zullen niet bestaan
# for elke order.
# -> Filter alle orders uit de grootboekrekening die niet in de
# DB voorkomen van die order.

# 2. model.getObligo / .geGeboekt ipv 1 kostenSoort
#    een lijst van KostenSoorten geven die in 1 MYSQL query gaat
#    NU doe ik 10 voor dezelfde order, dat zou ook bij elkaar moeten kunnen.
#    omdat we nu uitgaan van grootboek ipv ordernummers..
import web
import model
import GrootBoek


class Index:
    def __init__(self):
        pass

    @staticmethod
    def GET():
        maxdepth = 1
        grootboek = '28totaal4.txt'
        sapdatum = '25-5-2014'
        reserves = model.get_reserves()

        headers = ['Order', 'Stand op 1 jan', 'Bestedingsruimte']

        headersgrootboek = {}
        root = GrootBoek.load(0, grootboek)
        for child in root.children:
            headersgrootboek[child.name] = child.descr

        orders = []
        for order in model.get_orders():
            line = {}
            root = GrootBoek.load(order, grootboek)
            line['order'] = order
            line['reserve'] = reserves[str(order)]
            line['ruimte'] = -1*(root.totaalGeboektTree + root.totaalObligosTree)

            for child in root.children:
                line[child.name] = (-1*(child.totaalGeboektTree + child.totaalObligosTree))

            orders.append(line)

        return render.index(headers, headersgrootboek, orders, sapdatum, grootboek)


class View:
    def __init__(self):
        pass

    @staticmethod
    def GET(order):
        order = int(order)
        maxdepth = 4
        grootboek = '28totaal4.txt'
        sapdatum = '25-5-2014'
        root = GrootBoek.load(order, grootboek)

        htmlgrootboek = []
        for child in root.children:
            htmlgrootboek.append(child.html_tree(render, maxdepth, 0))

        totaal = -1*(root.totaalGeboektTree + root.totaalObligosTree)
        return render.view(order, grootboek, sapdatum, htmlgrootboek, totaal)


### Url mappings
urls = (
    '/', 'Index',
    '/view/(\d+)', 'View',
)

### Templates
t_globals = {
    'datestr': web.datestr
}
render = web.template.render('templates/')

app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()

import web
import os

def moneyfmt(value, places=0, curr='', sep=',', dp='',
             pos='', neg='-', trailneg='', keur=False):
#TODO fix import: import * niet toegestaan. moet dan in module.
    from decimal import *
    value = Decimal(value)
    """
    Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    >>> d = Decimal('-1234567.8901')
    >>> moneyfmt(d, curr='$')
    '-$1,234,567.89'
    >>> moneyfmt(d, places=0, sep='.', dp='', neg='', trailneg='-')
    '1.234.568-'
    >>> moneyfmt(d, curr='$', neg='(', trailneg=')')
    '($1,234,567.89)'
    >>> moneyfmt(Decimal(123456789), sep=' ')
    '123 456 789.00'
    >>> moneyfmt(Decimal('-0.02'), neg='<', trailneg='>')
    '<0.02>'

    """
    if keur:
        value = value / 1000
    q = Decimal(10) ** -places      # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))

# Opens and returns a graph as a data stream
def return_graph(jaar, tiepe, order):
    orderAllowed = True
    graphPath = config['graphPath'] +'%s/%s/%s.png' % (jaar, tiepe, order)

    if int(jaar) in range(1000, 9999):
        if os.path.isfile(graphPath):
            web.header("Content-Type", "images/png") # Set the Header
            return open(graphPath,"rb").read()
    else:
        raise web.notfound()

# Creates url to graph
# tiepes: realisatie, bars, pie
# names: anything from group orders to order numbers.
def generate_url(userHash, jaar, tiepe, name):
    return ('/graph/%s/%s/%s/%s.png' % (userHash, jaar, tiepe, name))

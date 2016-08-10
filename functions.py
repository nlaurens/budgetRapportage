from config import config
import model

def moneyfmt(value, places=0, curr='', sep=',', dp='',
             pos='', neg='-', trailneg='', keur=False):
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


# Checks if incoming IP is in
# allowed config range: True
# if not: False
def IpBlock(ip, ipRanges):
    from iptools import IpRangeList
    ipRanges = ipRanges.split()
    start = ipRanges[0:][::2]
    stop = ipRanges[1:][::2]

    for start,stop in zip(start,stop):
        ipRange = IpRangeList( (start,stop) )
        if ip in ipRange:
            return True
    return False

# Returns possible dropdown fills for web.py forms:
def get_dropdown_options():
    jarenDB = model.get_years_available()

    options = {}
    options['empty'] = [ ('', '')]
    options['all'] = [ ('*','! ALL !') ]
    options['years'] = zip(jarenDB, jarenDB)
    options['tables'] = config['mysql']['tables']['regels'].items()

    options['empty_years_all'] = options['empty'] + options['years'] + options['all']

    options['empty_tables'] = options['empty'] + options['tables'] 
    options['empty_tables_all'] = options['empty'] + options['tables'] + options['all']

    return options


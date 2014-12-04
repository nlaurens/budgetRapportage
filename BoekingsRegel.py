class BoekingsRegel():

    def __init__(self):
        self.order = 0
        self.kostensoort = 0
        self.naamkostensoort = ''
        self.omschrijving = ''
        self.datum = ''
        self.documentnummer = 0
        self.personeelsnummer = 0
        self.kosten = 0
        self.boekjar = 0
        self.periode = 0
        self.waarde = 0
        self.tiepe = ''  # Obligo / Geboekt

    def druk_af(self):
        print self.order
        print self.kostensoort
        print self.kosten
        print self.omschrijving



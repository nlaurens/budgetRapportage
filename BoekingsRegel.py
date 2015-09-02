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
        self.jaar = 0
        self.periode = 0
        self.waarde = 0
        self.tiepe = ''  # Obligo / Geboekt

    def druk_af(self):
        print self.order
        print self.kostensoort
        print self.kosten
        print self.omschrijving

    def copy(self):
        new = BoekingsRegel()
        new.order = self.order
        new.kostensoort = self.kostensoort
        new.naamkostensoort = self.naamkostensoort
        new.omschrijving = self.omschrijving
        new.datum = self.datum
        new.documentnummer = self.documentnummer
        new.personeelsnummer = self.personeelsnummer
        new.kosten = self.kosten
        new.jaar = self.jaar
        new.periode = self.periode
        new.waarde = self.waarde
        new.tiepe = self.tiepe


        return new


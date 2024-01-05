class AnalysisConfig:
    def __init__(self, ticker, period, interval, mav=None, volume=True, style='charles'):
        self.ticker = ticker
        self.period = period
        self.interval = interval
        self.mav = mav
        self.volume = volume
        self.style = style

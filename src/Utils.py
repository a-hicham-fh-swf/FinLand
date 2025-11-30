from datetime import datetime, timedelta

class Singleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

class TickerCache:
    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.cache.setdefault(None)
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, ticker):
        """Holt Daten aus dem Cache, wenn noch gültig"""
        if ticker in self.cache:
            data, timestamp = self.cache[ticker]
            if datetime.now() - timestamp < self.ttl:
                return data
        return None

    def set_ticker(self, ticker, data):
        """Speichert Daten mit aktuellem Zeitstempel"""
        self.cache[ticker] = (data, datetime.now())

    def set_tickers(self, tickers):
        """Speichert Daten in dem Cache"""
        if isinstance(tickers, dict):
            for ticker in tickers:
                self.set_ticker(ticker, tickers[ticker])

    def clear_ticker(self, ticker):
        """löscht den Eintrag mit dem Key ticker"""
        if ticker in self.cache:
            self.cache.pop(ticker)

    def clear(self):
        """Leert den gesamten Cache"""
        self.cache.clear()
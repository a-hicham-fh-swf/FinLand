from datetime import datetime, timedelta
import ticker_utils as tu

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

    def get(self, ticker, period, now=datetime.now()):
        """Holt Daten aus dem Cache, wenn noch gültig"""
        if ticker in self.cache:
            cached_data, cached_min_date, cached_timestamp = self.cache[ticker]
            min_date = tu.get_min_date_in_period_from_now(period, now)
            if now - cached_timestamp < self.ttl and min_date >= cached_min_date:
                return cached_data
        return None

    def set_ticker(self, ticker, data, min_date, now):
        """Speichert Daten mit aktuellem Zeitstempel"""
        self.cache[ticker] = (data, min_date, now)

    def set_tickers(self, tickers, period):
        """Speichert Daten in dem Cache"""
        if isinstance(tickers, dict):
            now = datetime.now()
            min_date = tu.get_min_date_in_period_from_now(period, now)
            for ticker in tickers:
                self.set_ticker(ticker, tickers[ticker], min_date, now)

    def clear_ticker(self, ticker):
        """löscht den Eintrag mit dem Key ticker"""
        if ticker in self.cache:
            self.cache.pop(ticker)

    def clear(self):
        """Leert den gesamten Cache"""
        self.cache.clear()
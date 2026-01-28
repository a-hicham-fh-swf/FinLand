from datetime import datetime, timedelta
import ticker_utils as tu

class Singleton:
    """
    Base class for the Singleton pattern.
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

class TickerCache:
    """
    Class for managing cached ticker data
    """
    def __init__(self, ttl_minutes=5):
        self.cache = {}
        self.cache.setdefault(None)
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, ticker, period, now=datetime.now()):
        """
        Gets the data for the provided ticker in the provided period from the cache if still valid

        Parameters
        ----------
        ticker : str
            The tickers to get the data for
        period : str
            The period to get the data for
        Returns
        -------
        DataFrame | None
            The found tickers data
        """
        if ticker in self.cache:
            cached_data, cached_min_date, cached_timestamp = self.cache[ticker]
            min_date = tu.get_min_date_in_period_from_now(period, now)
            if now - cached_timestamp < self.ttl and min_date >= cached_min_date:
                return cached_data
        return None

    def set_ticker(self, ticker, data, min_date, now):
        """
        Sets the provided data for the provided ticker for the provided period in the cache

        Parameters
        ----------
        ticker : str
            The ticker to set the data for
        data : pd.DataFrame
            The data to cache
        min_date : datetime.datetime
            The minimum date in the data
        now: datetime.datetime
            The time when the data was fetched
        """
        self.cache[ticker] = (data, min_date, now)

    def set_tickers(self, tickers, period):
        """
        Sets the provided data for the provided tickers for the provided period in the cache

        Parameters
        ----------
        tickers : str
            The tickers data
        period : str
            The period the data was watched for
        """
        if isinstance(tickers, dict):
            now = datetime.now()
            min_date = tu.get_min_date_in_period_from_now(period, now)
            for ticker in tickers:
                self.set_ticker(ticker, tickers[ticker], min_date, now)

    def clear_ticker(self, ticker):
        """
        Deletes the provided ticker data from the cache

        Parameters
        ----------
        ticker : str
            The ticker to delete from the cache
        """
        if ticker in self.cache:
            self.cache.pop(ticker)

    def clear(self):
        """
        Clears the whole cache
        """
        self.cache.clear()
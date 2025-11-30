import yfinance as yf
import math as m
import pandas as pd
from datetime import datetime
from tickerCache import TickerCache

# yf.enable_debug_mode()

def get_latest_close(ticker_data):
    return ticker_data['Close'].iloc[-1]

def get_interval_text(ticker_data):
    start_date = get_start_date(ticker_data)
    end_date = get_end_date(ticker_data)
    return f'vom {start_date.strftime("%d.%m.%Y")} bis {end_date.strftime("%d.%m.%Y")}'

def get_start_date(ticker_data):
    return ticker_data.index.min().date()

def get_end_date(ticker_data):
    return ticker_data.index.max().date()

def get_high_market_price(ticker_data):
    high_market_price_date = ticker_data['High'].idxmax()
    return ticker_data.loc[high_market_price_date]['High'], high_market_price_date

def get_low_market_price(ticker_data):
    low_market_price_date = ticker_data['Low'].idxmin()
    return ticker_data.loc[low_market_price_date]['Low'], low_market_price_date

def analyse(ticker_data):
    interval_text = get_interval_text(ticker_data)

    latest_market_price = get_latest_close(ticker_data)
    highest = get_high_market_price(ticker_data)
    lowest = get_low_market_price(ticker_data)

    print(f"Aktueller Schlusskurs ({ticker_data.index[-1].date()}): ${latest_market_price.item()}")
    print(f"Historischer Höchstkurs ({interval_text}): ${highest[0]} am {highest[1].strftime("%d.%m.%Y")}")
    print(f"Historischer Tiefstkurs ({interval_text}): ${lowest[0]} am {lowest[1].strftime("%d.%m.%Y")}")

    data_of_current_year = ticker_data[ticker_data.index.year == datetime.now().year]
    start_kurs = data_of_current_year.iloc[0]["Open"]
    performance = ((latest_market_price.item() - start_kurs.item()) / start_kurs.item()) * 100
    print(f"Performance seit Jahresbeginn (YTD): {performance:.2f}% (Startkurs: ${start_kurs.item()} - Schlusskurs: ${latest_market_price.item()})")

class Singleton:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

class TickerWrapper(Singleton):
    __ticker_cache = TickerCache()

    def __init__(self, ttl_minutes=3):
        self.__ticker_cache = TickerCache(ttl_minutes)
        pass

    def get_ticker_data(self, tickers, period='1y'):
        """
        Ruft Daten ab und berechnet einfache Statistiken für das letzte Jahr.
        """

        if not tickers:
            print(f"Bitte mindestens einen Ticker angeben.")
            return None

        if isinstance(tickers, str):
            tickers = [tickers]

        data = {ticker: self.__ticker_cache.get(ticker) for ticker in tickers}
        missing_tickers = [key for key, value in data.items() if value is None]

        if missing_tickers:
            try:
                fetched_data = yf.download(missing_tickers, period=period, group_by='ticker', rounding=True)
                updated_data = {missing_ticker: fetched_data[missing_ticker] for missing_ticker in missing_tickers}
                data.update(updated_data)
                self.__ticker_cache.set_tickers(updated_data)
            except Exception as e:
                print(f"Fehler beim Abruf der Daten: {e}")
                return None

        return data

myTicker = TickerWrapper()

while True:
    ticker_input = input("------------------------------------------------------------\nWelche Ticker sollen angezeigt werden? (z.B. AAPL, NVDA): ")

    if not ticker_input:
        break

    try:
        ticker_Data = myTicker.get_ticker_data([ticker.strip().upper() for ticker in ticker_input.split(",")])
        for ticker in ticker_Data:
            print(f"\nAktuelle Daten für {ticker}")
            analyse(ticker_Data[ticker])
    except Exception as e:
        print(f'Fehler beim Abfragen der Daten')
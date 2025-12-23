import yfinance as yf
from datetime import datetime
from Utils import Singleton, TickerCache
import TickerUtils as tu

# yf.enable_debug_mode()

def analyse(ticker_data):
    interval_text = tu.get_interval_text(ticker_data)

    latest_market_price = tu.get_latest_close(ticker_data)
    highest = tu.get_high_market_price(ticker_data)
    lowest = tu.get_low_market_price(ticker_data)

    data_of_current_year = ticker_data[ticker_data.index.year == datetime.now().year]
    start_market_price = data_of_current_year.iloc[0]["Open"]
    performance = ((latest_market_price.item() - start_market_price.item()) / start_market_price.item()) * 100

    print(f"Aktueller Schlusskurs ({ticker_data.index[-1].date()}): ${latest_market_price.item()}")
    print(f"Historischer Höchstkurs ({interval_text}): ${highest[0]} am {highest[1].strftime("%d.%m.%Y")}")
    print(f"Historischer Tiefstkurs ({interval_text}): ${lowest[0]} am {lowest[1].strftime("%d.%m.%Y")}")
    print(f"Performance seit Jahresbeginn (YTD): {performance:.2f}% (Startkurs: ${start_market_price.item()} - Schlusskurs: ${latest_market_price.item()})")

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

        data = {ticker: self.__ticker_cache.get(ticker, period) for ticker in tickers}
        missing_tickers = [key for key, value in data.items() if value is None]

        period = tu.get_next_suitable_period(period)

        if missing_tickers:
            try:
                fetched_data = yf.download(missing_tickers, period=period, group_by='ticker', rounding=True)
            except Exception as e:
                print(f"Fehler beim Abruf der Daten: {e}")
                return None

            updated_data = {missing_ticker: fetched_data[missing_ticker] for missing_ticker in missing_tickers}
            data.update(updated_data)
            self.__ticker_cache.set_tickers(updated_data, period)

        return data

myTicker = TickerWrapper()
"""
print(id(myTicker))
print(myTicker._TickerWrapper__ticker_cache.ttl)
myTicker2 = TickerWrapper(5)
print(id(myTicker2))
print(myTicker2._TickerWrapper__ticker_cache.ttl)
"""

while True:
    ticker_input = input("------------------------------------------------------------\nWelche Ticker sollen angezeigt werden? (z.B. AAPL, NVDA): ")
    if not ticker_input:
        break

    ticker_period = input("Für welchen Zeitraum in Monate? (keine oder eine ungültige Angabe ruft die Daten der letzten 12 Monate ab)")
    if not ticker_period.isdigit():
        ticker_period = "12"
    ticker_period += "mo"

    try:
        ticker_Data = myTicker.get_ticker_data([ticker.strip().upper() for ticker in ticker_input.split(",")], period=ticker_period)
        for ticker in ticker_Data:
            print(f"\nAktuelle Daten für {ticker}")
            analyse(ticker_Data[ticker])
    except Exception as e:
        print(f'Fehler beim Abfragen der Daten')
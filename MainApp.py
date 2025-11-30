import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# yf.enable_debug_mode()

class Singleton:
    __instance = None

    def __new__(self, *args, **kwargs):
        if not self.__instance:
            self.__instance = super().__new__(self)
        return self.__instance


class TickerWrapper(Singleton):
    ticker_dic = []

    def __init__(self):
        pass

    def analyse(self, ticker, period='1mo'):
        """
        Ruft Daten ab und berechnet einfache Statistiken für das letzte Jahr.
        """
        print(f"--- Analyse für Ticker: {ticker} ---")

        try:
            data = yf.download(ticker, period=period, rounding=True)
        except Exception as e:
            print(f"Fehler beim Abruf der Daten: {e}")
            return

        if data.empty:
            print(f"Keine Daten für Ticker {ticker} im angegebenen Zeitraum gefunden.")
            return

        start_date = data.index.min().date().strftime("%d.%m.%Y")
        end_date = data.index.max().date().strftime("%d.%m.%Y")

        interval_text = f'vom {start_date} bis {end_date}'

        # 2. Aktueller Kurs
        letzter_schlusskurs = data['Close'].iloc[-1]

        # 3. Einfache Statistiken (Höchst-/Tiefstkurs des letzten Jahres)
        max_kurs_idx = data['High'].idxmax()
        min_kurs_idx = data['Low'].idxmin()
        print(type(max_kurs_idx))

        # 4. Ausgabe
        print(f"Aktueller Schlusskurs ({data.index[-1].date()}): ${letzter_schlusskurs.item()}")
        print(f"Historischer Höchstkurs ({interval_text}): ${data.loc[max_kurs_idx]['High']} am {max_kurs_idx.iloc[0].strftime("%d.%m.%Y")}")
        #print(f"Historischer Tiefstkurs ({interval_text}): ${min_kurs.item()}")

        # Berechne die prozentuale Veränderung seit Jahresbeginn (YTD - Year To Date)
        data_of_current_year = data[data.index.year == datetime.now().year]
        first_row = data_of_current_year.iloc[0]
        start_kurs = data_of_current_year.iloc[0]["Open"]
        first_date = data_of_current_year.index[0]
        performance = ((letzter_schlusskurs.item() - start_kurs.item()) / start_kurs.item()) * 100
        print(f"Performance seit Jahresbeginn (YTD): {performance:.2f}% (Startkurs: ${start_kurs.item()} - Schlusskurs: ${letzter_schlusskurs.item()})")


#ticker_eingabe = input("Geben Sie einen Ticker ein (z.B. AAPL, BTC-USD): ").upper()
myTicker = TickerWrapper()
myTicker.analyse('AAPL')
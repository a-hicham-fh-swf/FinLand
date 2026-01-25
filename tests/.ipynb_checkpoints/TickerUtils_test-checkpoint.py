import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest
from unittest.mock import patch, MagicMock

# Importiere die Funktionen aus ticker_utils.py
# (Vorausgesetzt, die Datei ticker_utils.py liegt im selben Verzeichnis)
import TickerUtils as tu


# ----------------------------------------------------------------------
# 1. Fixture für Mock-Daten
# ----------------------------------------------------------------------

@pytest.fixture
def mock_ticker_data():
    """Erstellt ein deterministisches pandas DataFrame für Testzwecke."""
    data = {
        'Open': [100.0, 105.0, 110.0, 108.0, 115.0],
        'High': [106.0, 112.0, 115.0, 110.0, 120.0],  # Max: 120.0 am 2025-12-05
        'Low': [99.0, 104.0, 107.0, 98.0, 114.0],   # Min: 98.0 am 2025-12-04
        'Close': [105.0, 110.0, 108.0, 114.0, 118.0], # Letzter Schlusskurs: 118.0
        'Volume': [100000, 110000, 95000, 120000, 105000]
    }
    
    # Index mit Datetimes, um die Datumsfunktionen zu testen
    index = pd.to_datetime([
        '2025-12-01',
        '2025-12-02',
        '2025-12-03',
        '2025-12-04',
        '2025-12-05'
    ])
    df = pd.DataFrame(data, index=index)
    
    # Sicherstellen, dass der Close-Wert als Series mit 'item()' abrufbar ist, wie in main_app.py
    df['Close'].iloc[-1] = pd.Series([118.0], index=[df.index[-1]])
    return df


# ----------------------------------------------------------------------
# 2. Tests für Analysefunktionen (mit DataFrame Mocking)
# ----------------------------------------------------------------------

def test_get_latest_close(mock_ticker_data):
    """Testet den Abruf des letzten Schlusskurses."""
    latest_close = tu.get_latest_close(mock_ticker_data)
    assert latest_close.item() == 118.0

def test_get_high_market_price(mock_ticker_data):
    """Testet den Abruf des historischen Höchstkurses und des Datums."""
    price, date = tu.get_high_market_price(mock_ticker_data)
    assert price == 120.0
    assert date.strftime('%Y-%m-%d') == '2025-12-05'

def test_get_low_market_price(mock_ticker_data):
    """Testet den Abruf des historischen Tiefstkurses und des Datums."""
    price, date = tu.get_low_market_price(mock_ticker_data)
    assert price == 98.0
    assert date.strftime('%Y-%m-%d') == '2025-12-04'

def test_get_start_and_end_date(mock_ticker_data):
    """Testet den Abruf des Start- und Enddatums des Intervalls."""
    assert tu.get_start_date(mock_ticker_data).strftime('%Y-%m-%d') == '2025-12-01'
    assert tu.get_end_date(mock_ticker_data).strftime('%Y-%m-%d') == '2025-12-05'

def test_get_interval_text(mock_ticker_data):
    """Testet die korrekte Formatierung des Interval-Textes."""
    expected = 'vom 01.12.2025 bis 05.12.2025'
    assert tu.get_interval_text(mock_ticker_data) == expected


# ----------------------------------------------------------------------
# 3. Tests für get_next_suitable_period
# ----------------------------------------------------------------------

@pytest.mark.parametrize("input_period, expected_period", [
    # Tage (d)
    ('1d', '1d'),
    ('5d', '5d'),
    ('6d', '1mo'), # Rundet auf 1mo, da > 5d
    ('30d', '1mo'),
    # Monate (mo)
    ('1mo', '1mo'),
    ('2mo', '3mo'),
    ('3mo', '3mo'),
    ('4mo', '6mo'),
    ('6mo', '6mo'),
    ('7mo', '1y'), # Rundet auf 1y, da >= 7mo
    ('12mo', '1y'),
    ('13mo', '1y'),
    # Jahre (y)
    ('1y', '1y'),
    ('2y', '2y'),
    ('3y', '5y'), # Rundet auf 5y, da > 2y und < 5y
    ('5y', '5y'),
    ('6y', '10y'), # Rundet auf 10y, da > 5y und < 10y
    ('10y', '10y'),
    ('12y', None), # > 10y, fällt aus dem Schema und gibt None zurück
    # Sonderfälle
    ('ytd', 'ytd'),
    (None, None),
    ('', None),
    ('max', None),
])
def test_get_next_suitable_period_valid(input_period, expected_period):
    """Testet die korrekte Umwandlung einer beliebigen Periode in die geeignetste yfinance-Periode."""
    assert tu.get_next_suitable_period(input_period) == expected_period

@pytest.mark.parametrize("invalid_period", [
    '0mo',    # Nicht erlaubt durch Regex ([1-9]...)
    '1.5y',   # Kein Integer
    '1z',     # Ungültige Einheit
    'mo',     # Fehlender Wert
    '1'       # Fehlende Einheit
])
def test_get_next_suitable_period_invalid(invalid_period):
    """Testet, ob ungültige Eingaben eine ValueError-Exception auslösen."""
    with pytest.raises(ValueError, match='Invalid input'):
        tu.get_next_suitable_period(invalid_period)


# ----------------------------------------------------------------------
# 4. Tests für get_min_date_in_period_from_now (mit datetime Mocking)
# ----------------------------------------------------------------------

# Feste Zeitbasis für alle Tests, um sie deterministisch zu machen
MOCK_NOW = datetime(2025, 12, 15, 10, 30, 0, 123456)

@patch('TickerUtils.datetime')
@pytest.mark.parametrize("period, expected_date_str", [
    ('1d', '2025-12-14'), # 1 Tag zurück
    ('5d', '2025-12-10'), # 5 Tage zurück
    ('1mo', '2025-11-15'), # 1 Monat zurück
    ('3mo', '2025-09-15'), # 3 Monate zurück
    ('6mo', '2025-06-15'), # 6 Monate zurück
    ('1y', '2024-12-15'), # 1 Jahr zurück
    ('2y', '2023-12-15'), # 2 Jahre zurück
    ('5y', '2020-12-15'), # 5 Jahre zurück
    ('10y', '2015-12-15'), # 10 Jahre zurück
    ('ytd', '2025-01-01'), # Jahresanfang (Year To Date)
])
def test_get_min_date_in_period_from_now(mock_datetime, period, expected_date_str):
    """Testet, ob das korrekte Startdatum basierend auf der Periode berechnet wird."""
    
    # Mocken von datetime.now(), um MOCK_NOW als "jetzt" zu verwenden
    mock_datetime.now.return_value = MOCK_NOW
    # Manchmal muss das datetime-Objekt selbst gemockt werden, um Konstruktor-Aufrufe zu handhaben (speziell für 'ytd')
    mock_datetime.datetime = MagicMock(side_effect=lambda *args, **kwargs: datetime(*args, **kwargs))
    mock_datetime.datetime.now.return_value = MOCK_NOW
    
    # Aufruf der Funktion
    # Wichtig: Die Funktion ruft intern tu.get_next_suitable_period auf, was hier explizit getestet wird.
    min_date = tu.get_min_date_in_period_from_now(period, MOCK_NOW)

    # Überprüfung des Datums (nur Jahr, Monat, Tag)
    assert min_date.strftime('%Y-%m-%d') == expected_date_str
    
    # Überprüfung, dass die Zeit auf Mitternacht zurückgesetzt wurde
    assert min_date.hour == 0
    assert min_date.minute == 0
    assert min_date.second == 0
    assert min_date.microsecond == 0
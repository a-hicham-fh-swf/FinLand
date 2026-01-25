import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# ... (Setup-Code unverändert) ...

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    import TickerUtils as tu
except ImportError as e:
    print(f"Fehler beim Import von TickerUtils: {e}")
    raise


# ----------------------------------------------------------------------
# 1. Fixture für Mock-Daten (unverändert)
# ----------------------------------------------------------------------
@pytest.fixture
def mock_ticker_data():
    """Erstellt ein deterministisches pandas DataFrame für Testzwecke."""
    data = {
        'Open': [100.0, 105.0, 110.0, 108.0, 115.0],
        'High': [106.0, 112.0, 115.0, 110.0, 120.0],
        'Low': [99.0, 104.0, 107.0, 98.0, 114.0],
        'Close': [105.0, 110.0, 108.0, 114.0, 118.0],
        'Volume': [100000, 110000, 95000, 120000, 105000]
    }
    index = pd.to_datetime([
        '2025-12-01', '2025-12-02', '2025-12-03', '2025-12-04', '2025-12-05'
    ])
    df = pd.DataFrame(data, index=index)
    df['Close'].iloc[-1] = pd.Series([118.0], index=[df.index[-1]])
    return df


# ----------------------------------------------------------------------
# 2. Tests für Analysefunktionen (mit verbesserter Assertion-Meldung)
# ----------------------------------------------------------------------

def test_get_latest_close(mock_ticker_data):
    """Testet den Abruf des letzten Schlusskurses."""
    latest_close = tu.get_latest_close(mock_ticker_data)
    # Hinzugefügte Meldung für den Fehlerfall (der Teil nach dem Komma)
    assert latest_close.item() == 118.0, f"Erwarteter Close ist 118.0, aber {latest_close.item()} wurde gefunden."


def test_get_high_market_price(mock_ticker_data):
    """Testet den Abruf des historischen Höchstkurses und des Datums."""
    price, date = tu.get_high_market_price(mock_ticker_data)
    assert price == 120.0, f"Höchstpreis sollte 120.0 sein, ist aber {price}."
    assert date.strftime(
        '%Y-%m-%d') == '2025-12-05', f"Datum des Höchstpreises ist falsch: {date.strftime('%Y-%m-%d')}."


def test_get_low_market_price(mock_ticker_data):
    """Testet den Abruf des historischen Tiefstkurses und des Datums."""
    price, date = tu.get_low_market_price(mock_ticker_data)
    assert price == 98.0, f"Tiefstpreis sollte 98.0 sein, ist aber {price}."
    assert date.strftime(
        '%Y-%m-%d') == '2025-12-04', f"Datum des Tiefstpreises ist falsch: {date.strftime('%Y-%m-%d')}."


def test_get_start_and_end_date(mock_ticker_data):
    """Testet den Abruf des Start- und Enddatums des Intervalls."""
    start_date = tu.get_start_date(mock_ticker_data).strftime('%Y-%m-%d')
    end_date = tu.get_end_date(mock_ticker_data).strftime('%Y-%m-%d')

    assert start_date == '2025-12-01', f"Startdatum ist falsch: {start_date}."
    assert end_date == '2025-12-05', f"Enddatum ist falsch: {end_date}."


def test_get_interval_text(mock_ticker_data):
    """Testet die korrekte Formatierung des Interval-Textes."""
    expected = 'vom 01.12.2025 bis 05.12.2025'
    actual = tu.get_interval_text(mock_ticker_data)
    assert actual == expected, f"Interval-Text ist falsch formatiert. Erwartet: '{expected}', Gefunden: '{actual}'."


# ----------------------------------------------------------------------
# 3. Tests für get_next_suitable_period (Assertions unverändert, da Fehler von Pytest gut gemeldet werden)
# ----------------------------------------------------------------------

@pytest.mark.parametrize("input_period, expected_period", [
    ('1d', '1d'), ('5d', '5d'), ('6d', '1mo'), ('30d', '1mo'),
    ('1mo', '1mo'), ('2mo', '3mo'), ('3mo', '3mo'), ('4mo', '6mo'),
    ('6mo', '6mo'), ('7mo', '1y'), ('12mo', '1y'), ('13mo', '1y'),
    ('1y', '1y'), ('2y', '2y'), ('3y', '5y'), ('5y', '5y'),
    ('6y', '10y'), ('10y', '10y'), ('12y', None),
    ('ytd', 'ytd'), (None, None), ('', None), ('max', None),
])
def test_get_next_suitable_period_valid(input_period, expected_period):
    """Testet die korrekte Umwandlung einer beliebigen Periode in die geeignetste yfinance-Periode."""
    actual = tu.get_next_suitable_period(input_period)
    assert actual == expected_period, f"Periode '{input_period}' sollte '{expected_period}' ergeben, fand aber '{actual}'."


@pytest.mark.parametrize("invalid_period", [
    '0mo', '1.5y', '1z', 'mo', '1'
])
def test_get_next_suitable_period_invalid(invalid_period):
    """Testet, ob ungültige Eingaben eine ValueError-Exception auslösen."""
    with pytest.raises(ValueError, match='Invalid input'):
        tu.get_next_suitable_period(invalid_period)


# ----------------------------------------------------------------------
# 4. Tests für get_min_date_in_period_from_now (mit datetime Mocking)
# ----------------------------------------------------------------------

MOCK_NOW = datetime(2025, 12, 15, 10, 30, 0, 123456)


@patch('TickerUtils.datetime')
@pytest.mark.parametrize("period, expected_date_str", [
    ('1d', '2025-12-14'), ('5d', '2025-12-10'), ('1mo', '2025-11-15'),
    ('3mo', '2025-09-15'), ('6mo', '2025-06-15'), ('1y', '2024-12-15'),
    ('2y', '2023-12-15'), ('5y', '2020-12-15'), ('10y', '2015-12-15'),
    ('ytd', '2025-01-01'),
])
def test_get_min_date_in_period_from_now(mock_datetime, period, expected_date_str):
    """Testet, ob das korrekte Startdatum basierend auf der Periode berechnet wird."""

    # ... (Mocking-Setup unverändert) ...
    mock_datetime.now.return_value = MOCK_NOW
    mock_datetime.datetime = MagicMock(side_effect=lambda *args, **kwargs: datetime(*args, **kwargs))
    mock_datetime.datetime.now.return_value = MOCK_NOW

    min_date = tu.get_min_date_in_period_from_now(period, MOCK_NOW)

    # Verbessertes Assertion für das Datum
    actual_date_str = min_date.strftime('%Y-%m-%d')
    assert actual_date_str == expected_date_str, \
        f"Periode '{period}': Erwartetes Startdatum {expected_date_str}, aber {actual_date_str} gefunden."

    # Verbessertes Assertion für die Uhrzeit
    assert min_date.hour == 0 and min_date.minute == 0 and min_date.second == 0 and min_date.microsecond == 0, \
        f"Die Zeit wurde nicht korrekt auf Mitternacht zurückgesetzt: {min_date.time()}."
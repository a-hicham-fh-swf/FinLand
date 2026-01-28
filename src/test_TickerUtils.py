import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import patch
import ticker_utils as tu


# zentrale Testdatenverwaltung

@pytest.fixture
def sample_stock_data():
    """
    Erzeugt einen Test-DataFrame.
    """
    dates = pd.date_range(start="2025-01-01", periods=5, freq="D")
    data = {
        'Close': [100.0, 105.0, 102.0, 110.0, 108.0],
        'High': [102.0, 106.0, 104.0, 112.0, 110.0],
        'Low': [98.0, 103.0, 100.0, 108.0, 107.0]
    }
    return pd.DataFrame(data, index=dates)


# --- TESTS FÜR MODUL 4.1 (TickerUtils) ---

def test_TC_TU_001_latest_close(sample_stock_data):
    """Prüft, ob der allerletzte verfügbare Close-Preis extrahiert wird."""
    result = tu.get_latest_close(sample_stock_data)
    assert result == 108.0


def test_TC_TU_002_high_market_price(sample_stock_data):
    """Prüft die Ermittlung des Höchstkurses inkl. des korrekten Datums."""
    price, date = tu.get_high_market_price(sample_stock_data)
    assert price == 112.0
    assert date == pd.Timestamp("2025-01-04")


def test_TC_TU_003_low_market_price(sample_stock_data):
    """
    Prüft die Ermittlung des Tiefstkurses inkl. Zeitstempel.
    """
    price, date = tu.get_low_market_price(sample_stock_data)

    assert price == 98.0
    assert date == pd.Timestamp("2025-01-01")
def test_TC_TU_004_interval_text(sample_stock_data):
    """Prüft die korrekte Datumsformatierung für die Anzeige in der UI."""
    # Erwartet: "vom 01.01.2025 bis 05.01.2025"
    result = tu.get_interval_text(sample_stock_data)
    assert "01.01.2025" in result
    assert "05.01.2025" in result


@pytest.mark.parametrize("period_in, expected", [
    ("1d", "1d"), ("3d", "5d"), ("10d", "1mo"),
    ("4mo", "6mo"), ("1y", "1y"), ("ytd", "ytd")
])
def test_TC_TU_005_suitable_period_mapping(period_in, expected):
    """
    Mapping-Logik-Test:
    krumme Zeiträume führen zu einem passenden Ergebnis.
    """
    assert tu.get_next_suitable_period(period_in) == expected


def test_TC_TU_006_invalid_period():
    """Prüft die Robustheit gegen falsche String-Eingaben."""
    with pytest.raises(ValueError, match="Invalid input"):
        tu.get_next_suitable_period("invalid_string")



FIXED_NOW = datetime(2025, 12, 15, 14, 30, 0)


@pytest.mark.parametrize("period, expected_date", [
    ("1d", datetime(2025, 12, 14, 0, 0, 0)),
    ("5d", datetime(2025, 12, 10, 0, 0, 0)),
    ("1mo", datetime(2025, 11, 15, 0, 0, 0)),
    ("3mo", datetime(2025, 9, 15, 0, 0, 0)),
    ("6mo", datetime(2025, 6, 15, 0, 0, 0)),
    ("1y", datetime(2024, 12, 15, 0, 0, 0)),
    ("2y", datetime(2023, 12, 15, 0, 0, 0)),
    ("5y", datetime(2020, 12, 15, 0, 0, 0)),
    ("10y", datetime(2015, 12, 15, 0, 0, 0)),
])
def test_TC_TU_007_min_date_calculation(period, expected_date):
    """
    Behebt den 'Fixture not found' Fehler durch korrekte Parameter-Injektion.
    """
    # Die Funktion get_min_date_in_period_from_now berechnet das Startdatum
    result = tu.get_min_date_in_period_from_now(period, FIXED_NOW)

    # Validierung: Zeitanteile auf 00:00:00 prüfen, wie in ticker_utils implementiert
    assert result == expected_date

def test_TC_TU_008_ytd_logic():
    """Prüft den YTD-Spezialfall (immer 1. Januar des aktuellen Jahres)."""
    fixed_now = datetime(2025, 5, 20)
    result = tu.get_min_date_in_period_from_now("ytd", fixed_now)
    assert result == datetime(2025, 1, 1)


def test_TC_TU_009_empty_dataframe():
    """
    TC_TU_009 – Empty DataFrame
    Prüft das Verhalten des Systems, wenn keine Daten gefunden wurden.

    """
    empty_df = pd.DataFrame(columns=['Close', 'High', 'Low', 'Open'])

    # 1. Fall: Zugriff auf .iloc[-1] bei leerem Close
    with pytest.raises(IndexError):
        tu.get_latest_close(empty_df)

    # 2. Fall: .idxmax() auf leere Spalte High
    with pytest.raises(ValueError):
        tu.get_high_market_price(empty_df)


def test_TC_TU_010_missing_columns():
    """Negative Test: Wie reagiert das System auf unvollständige Daten?"""
    df_empty = pd.DataFrame({'Open': [1, 2]})
    with pytest.raises(KeyError):
        tu.get_latest_close(df_empty)
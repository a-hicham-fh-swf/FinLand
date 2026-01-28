import pytest
from datetime import datetime, timedelta
from utils import Singleton, TickerCache


# --- SINGLETON TEST ---

class DatabaseConnection(Singleton):
    pass


def test_TC_U_001_singleton_identity():
    """Prüft, ob das Singleton-Pattern wirklich nur eine Instanz zulässt."""
    s1 = DatabaseConnection()
    s2 = DatabaseConnection()
    # In einer Präsentation: 'Beide Variablen zeigen auf die exakt selbe Speicheradresse'
    assert s1 is s2


# --- CACHE TESTS ---

def test_TC_U_002_cache_set_get_valid():
    """Prüft, ob Daten im Cache gespeichert und korrekt abgerufen werden können."""
    cache = TickerCache(ttl_minutes=5)
    now = datetime.now()
    data = {"price": 100}
    # Wir speichern Daten für den Ticker 'AAPL' ab einem bestimmten min_date
    cache.set_ticker("AAPL", data, datetime(2024, 1, 1), now)

    # Abruf innerhalb der TTL und mit passendem Zeitraum
    result = cache.get("AAPL", "1y", now=now)
    assert result == data


def test_TC_U_003_cache_expiration():
    """Prüft, ob der Cache nach Ablauf der TTL (Time To Live) 'None' liefert."""
    cache = TickerCache(ttl_minutes=1)  # 1 Minute Gültigkeit
    start_time = datetime(2025, 1, 1, 12, 0)
    data = "Geheime Daten"

    cache.set_ticker("MSFT", data, datetime(2024, 1, 1), start_time)

    # Simulierter Abruf 61 Sekunden später
    future_time = start_time + timedelta(seconds=61)
    result = cache.get("MSFT", "1y", now=future_time)

    assert result is None  # Daten müssen abgelaufen sein


def test_TC_U_004_cache_miss_incompatible_period():
    """
    TC_U_004 – Cache miss wenn Periode nicht passt.

    """
    cache = TickerCache(ttl_minutes=5)
    now = datetime(2025, 1, 10, 12, 0)

    # Wir speichern Daten, die nur 5 Tage zurückreichen (ab 5. Jan)
    cached_min_date = datetime(2025, 1, 5)
    cache.set_ticker("AAPL", {"data": "5d_data"}, cached_min_date, now)

    # Request: Nutzer möchte nun '1mo' (ca. 30 Tage zurück, ab 11. Dez)
    # Da 11. Dez (erforderlich) VOR dem 5. Jan (vorhanden) liegt,
    # muss die Logik 'min_date >= cached_min_date' fehlschlagen.
    result = cache.get("AAPL", "1mo", now=now)

    assert result is None, "Cache hätte None liefern müssen, da Zeitraum zu klein"
def test_TC_U_005_cache_miss_restrictive_date():
    """
    Testet das 'Daten-Loch' Szenario:
    Wenn der Cache Daten ab 2024 hat, der User aber Daten ab 2023 will,
    darf der Cache nichts zurückgeben.
    """
    cache = TickerCache(ttl_minutes=60)
    now = datetime(2025, 1, 1)

    # Im Cache liegen nur Daten für das letzte Jahr (ab 2024)
    cache.set_ticker("TSLA", "Data2024", datetime(2024, 1, 1), now)

    # Request nach 2 Jahren ("2y" führt zu min_date 2023)
    # Da 2023 vor 2024 liegt, fehlen dem Cache Daten -> Cache Miss
    result = cache.get("TSLA", "2y", now=now)

    assert result is None
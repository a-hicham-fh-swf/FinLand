import sys
import types

# ------------------------------------------------------------
# STUB: yfinance ersetzen, damit src/data_service.py importierbar ist
# (ohne curl_cffi / native libs wie libidn2)
#
# Hintergrund:
# Beim Import von data_service wird "import yfinance as yf" ausgeführt.
# Auf deinem System crasht das wegen einer fehlenden nativen Library.
#
# Lösung für Unit-Tests:
# Wir stellen im Test ein Fake-Modul "yfinance" bereit, bevor data_service importiert wird.
# ------------------------------------------------------------
fake_yfinance = types.ModuleType("yfinance")


def _download_stub(*_args, **_kwargs):
    raise RuntimeError(
        "yfinance.download wurde im Test-Stub aufgerufen. "
        "In Tests muss yf.download immer gemockt werden."
    )


class _TickerStub:
    def __init__(self, *_args, **_kwargs):
        # Standardwerte (werden in Tests gezielt überschrieben / gemockt)
        self.news = []
        self.info = {}


fake_yfinance.download = _download_stub
fake_yfinance.Ticker = _TickerStub

# yfinance in sys.modules registrieren, BEVOR data_service importiert wird
sys.modules["yfinance"] = fake_yfinance

# ------------------------------------------------------------
# Ab hier normale Test-Imports
# ------------------------------------------------------------
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

import utils
import data_service as ds


# ----------------------------
# WICHTIG: Test-Isolation
# ----------------------------
@pytest.fixture(autouse=True)
def _reset_singleton_and_cache():
    """
    GIVEN: TickerWrapper basiert auf einem Singleton-Pattern (eine Instanz global).
    WHEN: pytest mehrere Tests nacheinander ausführt,
    THEN: dürfen sich Tests nicht gegenseitig beeinflussen.

    -> Deshalb setzen wir die Singleton-Instanz vor und nach JEDEM Test zurück.
    """
    utils.Singleton._Singleton__instance = None
    yield
    utils.Singleton._Singleton__instance = None


def _sample_singleindex_df():
    """Hilfsfunktion: kleines, typisches Kurs-DataFrame (SingleIndex-Spalten)."""
    idx = pd.to_datetime(["2025-01-01", "2025-01-02"])
    return pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.5, 12.5],
            "Volume": [1000, 1100],
        },
        index=idx,
    )


# ============================================================
# Kapitel 4.3 – DataService (TC_DS_001 bis TC_DS_008)
# ============================================================

def test_TC_DS_001_normalize_history_frame_singleindex_unchanged():
    # GIVEN: ein normales DataFrame (SingleIndex), wie typische Kursdaten
    df = _sample_singleindex_df()

    # WHEN: ich normalisiere die Daten für einen Ticker
    result = ds._normalize_history_frame(df, ticker="AAPL")

    # THEN: die Daten bleiben unverändert (weil keine MultiIndex-Struktur vorliegt)
    assert result is not None
    assert list(result.columns) == list(df.columns)
    pd.testing.assert_frame_equal(result, df)


def test_TC_DS_002_normalize_history_frame_multiindex_extracts_one_ticker():
    # GIVEN: yfinance liefert beim Multi-Ticker-Download häufig MultiIndex-Spalten:
    #        Level 0 = Ticker (AAPL, MSFT), Level 1 = OHLCV
    idx = pd.to_datetime(["2025-01-01", "2025-01-02"])
    cols = pd.MultiIndex.from_product([["AAPL", "MSFT"], ["Open", "Close", "Volume"]])

    fetched = pd.DataFrame(
        [
            [10, 11, 1000, 20, 21, 2000],
            [12, 13, 1100, 22, 23, 2100],
        ],
        index=idx,
        columns=cols,
    )

    # WHEN: ich normalisiere für genau einen Ticker (AAPL)
    result = ds._normalize_history_frame(fetched, ticker="AAPL")

    # THEN: ich erhalte ein flaches DataFrame NUR für AAPL (Spalten: Open/Close/Volume)
    assert result is not None
    assert list(result.columns) == ["Open", "Close", "Volume"]
    assert result.loc[pd.Timestamp("2025-01-01"), "Close"] == 11
    assert result.loc[pd.Timestamp("2025-01-02"), "Volume"] == 1100


def test_TC_DS_003_get_ticker_data_cache_hit_no_yfinance_download():
    # GIVEN: Im Cache liegt bereits ein gültiges DataFrame für AAPL
    wrapper = ds.TickerWrapper()

    cache_mock = MagicMock()
    cache_mock.get.return_value = _sample_singleindex_df()
    wrapper._TickerWrapper__ticker_cache = cache_mock  # private Variable gezielt ersetzen

    # WHEN: ich rufe get_ticker_data auf
    with patch("data_service.yf.download") as download_mock:
        data = wrapper.get_ticker_data(["AAPL"], period="1y")

    # THEN: yfinance darf NICHT aufgerufen werden (Cache Hit)
    download_mock.assert_not_called()
    assert "AAPL" in data
    assert data["AAPL"] is not None
    assert list(data["AAPL"].columns) == ["Open", "High", "Low", "Close", "Volume"]


def test_TC_DS_004_get_ticker_data_cache_miss_downloads_and_caches():
    # GIVEN: Cache liefert nichts (Miss) -> yfinance muss laden
    wrapper = ds.TickerWrapper()

    cache_mock = MagicMock()
    cache_mock.get.return_value = None
    wrapper._TickerWrapper__ticker_cache = cache_mock

    fetched = _sample_singleindex_df()

    # WHEN: get_ticker_data wird aufgerufen und yfinance liefert Daten
    with patch("data_service.yf.download", return_value=fetched) as download_mock:
        data = wrapper.get_ticker_data(["AAPL"], period="1y")

    # THEN:
    # 1) yfinance wurde aufgerufen
    download_mock.assert_called_once()

    # 2) Cache wurde mit set_tickers(...) befüllt
    cache_mock.set_tickers.assert_called_once()
    updated_dict = cache_mock.set_tickers.call_args[0][0]
    assert isinstance(updated_dict, dict)
    assert "AAPL" in updated_dict
    assert updated_dict["AAPL"] is not None

    # 3) Rückgabe enthält die Daten
    assert "AAPL" in data
    assert data["AAPL"] is not None


def test_TC_DS_005_get_ticker_data_yfinance_returns_empty_dataframe_becomes_none():
    # GIVEN: Cache Miss und yfinance liefert ein leeres DataFrame
    wrapper = ds.TickerWrapper()

    cache_mock = MagicMock()
    cache_mock.get.return_value = None
    wrapper._TickerWrapper__ticker_cache = cache_mock

    empty = pd.DataFrame()

    # WHEN: get_ticker_data wird ausgeführt
    with patch("data_service.yf.download", return_value=empty):
        data = wrapper.get_ticker_data(["AAPL"], period="1y")

    # THEN: Normalisierung macht daraus None (weil empty => None)
    assert "AAPL" in data
    assert data["AAPL"] is None

    # UND: Cache wird trotzdem aktualisiert (mit None als Wert)
    cache_mock.set_tickers.assert_called_once()
    updated_dict = cache_mock.set_tickers.call_args[0][0]
    assert updated_dict["AAPL"] is None


def test_TC_DS_006_get_news_yfinance_has_news_no_rss_fallback():
    # GIVEN: yfinance liefert direkt News-Items
    wrapper = ds.TickerWrapper()
    yfinance_news = [{"title": "News 1"}, {"title": "News 2"}]

    ticker_obj = MagicMock()
    ticker_obj.news = yfinance_news

    # WHEN: get_news wird aufgerufen
    with patch("data_service.yf.Ticker", return_value=ticker_obj):
        with patch("data_service._google_news_rss") as rss_mock:
            out = wrapper.get_news("AAPL", limit=10)

    # THEN: RSS-Fallback darf NICHT verwendet werden, yfinance-News werden zurückgegeben
    rss_mock.assert_not_called()
    assert out == yfinance_news


def test_TC_DS_007_get_news_yfinance_empty_uses_rss_fallback():
    # GIVEN: yfinance liefert keine News -> Fallback muss greifen
    wrapper = ds.TickerWrapper()

    ticker_obj = MagicMock()
    ticker_obj.news = []  # keine News über yfinance
    ticker_obj.info = {"shortName": "Apple Inc"}  # wird für Query genutzt ("Apple Inc stock")

    rss_items = [
        {"title": "RSS News", "link": "http://x", "publisherPublishTime": None, "source": "Google News"}
    ]

    # WHEN: get_news wird aufgerufen und RSS liefert Ergebnisse
    with patch("data_service.yf.Ticker", return_value=ticker_obj):
        with patch("data_service._google_news_rss", return_value=rss_items) as rss_mock:
            out = wrapper.get_news("AAPL", limit=10)

    # THEN: RSS wurde aufgerufen und Ergebnis kommt aus dem Fallback
    assert rss_mock.called
    assert isinstance(out, list)
    assert len(out) >= 1
    assert out[0]["title"] == "RSS News"


def test_TC_DS_008_google_news_rss_uses_quote_plus_url_encoding():
    # GIVEN: Query enthält Sonderzeichen und Leerzeichen (kritisch für URLs)
    query = "S&P 500"

    # WHEN: _google_news_rss baut die URL und ruft feedparser.parse(url) auf
    with patch("data_service.feedparser.parse") as parse_mock:
        parse_mock.return_value.entries = []  # kein echtes Netz, nur kontrollierter Test
        ds._google_news_rss(query)

    # THEN: URL muss encoded sein: & -> %26 und Leerzeichen -> +
    assert parse_mock.called
    called_url = parse_mock.call_args[0][0]
    assert "S%26P+500" in called_url

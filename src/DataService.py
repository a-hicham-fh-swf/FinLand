import yfinance as yf
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus  # <-- WICHTIG
import feedparser

from Utils import Singleton, TickerCache
import TickerUtils as tu


def _google_news_rss(query: str, lang="de", country="DE"):
    q = quote_plus(query)
    url = f"https://news.google.com/rss/search?q={q}&hl={lang}-{country}&gl={country}&ceid={country}:{lang}"
    feed = feedparser.parse(url)

    items = []
    for e in feed.entries[:20]:
        published = None
        if getattr(e, "published_parsed", None):
            published = datetime(*e.published_parsed[:6])

        items.append({
            "title": getattr(e, "title", "") or "(ohne Titel)",
            "link": getattr(e, "link", ""),
            "publisherPublishTime": int(published.timestamp()) if published else None,
            "source": getattr(getattr(e, "source", None), "title", None) or "Google News",
        })
    return items


def _normalize_history_frame(fetched: pd.DataFrame, ticker: str) -> pd.DataFrame | None:
    if fetched is None or fetched.empty:
        return None

    cols = fetched.columns

    if isinstance(cols, pd.MultiIndex):
        if ticker in cols.get_level_values(0):
            df = fetched[ticker]
        elif ticker in cols.get_level_values(1):
            df = fetched.xs(ticker, level=1, axis=1)
        else:
            df = fetched

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna(how="all")
        return df if not df.empty else None

    df = fetched.dropna(how="all")
    return df if not df.empty else None


class TickerWrapper(Singleton):
    def __init__(self, ttl_minutes=3):
        self.__ticker_cache = TickerCache(ttl_minutes)

    def get_ticker_data(self, tickers, period="1y"):
        if not tickers:
            return {}

        if isinstance(tickers, str):
            tickers = [tickers]

        tickers = [t.strip().upper() for t in tickers if t.strip()]
        if not tickers:
            return {}

        period = tu.get_next_suitable_period(period) or "1y"

        now = datetime.now()
        data = {t: self.__ticker_cache.get(t, period, now) for t in tickers}
        missing = [t for t, v in data.items() if v is None]

        if missing:
            try:
                fetched = yf.download(
                    missing,
                    period=period,
                    group_by="ticker",
                    rounding=True,
                    progress=False,
                    auto_adjust=False,
                )
            except Exception:
                return data

            updated = {t: _normalize_history_frame(fetched, t) for t in missing}
            data.update(updated)
            self.__ticker_cache.set_tickers(updated, period)

        return data

    def get_ticker_data_by_dates(self, tickers, start_date, end_date):
        if isinstance(tickers, str):
            tickers = [tickers]
        tickers = [t.strip().upper() for t in tickers if t.strip()]
        if not tickers:
            return {}

        try:
            fetched = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                group_by="ticker",
                rounding=True,
                progress=False,
                auto_adjust=False,
            )
        except Exception:
            return {}

        return {t: _normalize_history_frame(fetched, t) for t in tickers}

    def get_info(self, ticker):
        try:
            return yf.Ticker(ticker).info or {}
        except Exception:
            return {}

    def get_news(self, ticker, limit=10):
        # 1) yfinance zuerst
        try:
            news = yf.Ticker(ticker).news or []
            if news:
                return news[:limit]
        except Exception:
            pass

        # 2) Fallback: Google News RSS (Company + Ticker)
        company = ""
        try:
            info = yf.Ticker(ticker).info or {}
            company = (info.get("shortName") or info.get("longName") or "").strip()
        except Exception:
            company = ""

        queries = []
        if company:
            queries.append(f"{company} stock")
        queries.append(f"{ticker} stock")

        results = []
        seen = set()
        for q in queries:
            for item in _google_news_rss(q, lang="de", country="DE"):
                key = (item.get("title"), item.get("link"))
                if key in seen:
                    continue
                seen.add(key)
                results.append(item)
                if len(results) >= limit:
                    return results[:limit]

        return results[:limit]

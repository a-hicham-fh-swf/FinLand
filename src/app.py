import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_searchbox import st_searchbox
from data_service import TickerWrapper
import ticker_utils as tu
from ui_logic import fmt, format_percent_change, should_show_chart

st.set_page_config(page_title="Aktien Dashboard", layout="wide")
service = TickerWrapper(ttl_minutes=3)
st.title("📈 Aktien Dashboard")

if "tickers" not in st.session_state:
    st.session_state.tickers = set()
tickers = st.session_state.tickers

# ---------------- Sidebar Controls ----------------
with st.sidebar:
    st.header("Einstellungen")

    selected = st_searchbox(
        service.get_company_name_and_symbol,
        key="ticker_search",
        placeholder="Unternehmensname...",
        label="Unternehmen",
        clear_on_submit=True
    )

    if selected and selected['symbol']:
        symbol = selected['symbol']
        #current_tickers = st.session_state.tickers_raw.split(',')
        #current_tickers = [t.strip() for t in current_tickers if t.strip()]

        tickers.add(symbol)

    #tickers_raw = st.text_input(label="Ticker (kommagetrennt)", key="tickers_raw")
    #tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]

    period_label = st.selectbox("Periode", ["1D", "5D", "1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "YTD", "MAX"], index=3)
    period_map = {"1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y", "5Y": "5y", "10Y": "10y", "YTD": "ytd", "MAX": "max"}
    period = period_map[period_label]

    st.markdown("---")
    st.subheader("Alternativ: Start/Ende (optional)")
    use_dates = st.checkbox("Start/Ende verwenden", value=False)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Von", value=datetime(datetime.now().year, 1, 1), format="DD.MM.YYYY")
    with col_d2:
        end_date = st.date_input("Bis", value=datetime.now(), format="DD.MM.YYYY")

    st.markdown("---")
    st.subheader("Ticker-Auswahl (für Chart/KPIs)")
    # wird später gefüllt, sobald Daten da sind


# ---------------- Data Load ----------------
if not tickers:
    st.info("Bitte mindestens einen Ticker eingeben (z.B. AAPL, NVDA).")
    st.stop()

@st.cache_data(ttl=60, show_spinner=False)
def load_data_cached(tickers_tuple, period, use_dates, start_str, end_str):
    tickers_list = list(tickers_tuple)
    if use_dates:
        data = service.get_ticker_data_by_dates(tickers_tuple, start_str, end_str)
    else:
        data = service.get_ticker_data(tickers_tuple, period=period)

    info = {t: service.get_info(t) for t in tickers_tuple}
    news = {t: service.get_news(t, limit=10) for t in tickers_tuple}
    return data, info, news

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

with st.spinner("Lade Marktdaten…"):
    data, info, news = load_data_cached(tickers, period, use_dates, start_str, end_str)

available_tickers = [t for t in tickers if data.get(t) is not None and not data.get(t).empty]
missing_tickers = [t for t in tickers if t not in available_tickers]

if missing_tickers:
    st.warning(f"Keine/ungültige Daten für: {', '.join(missing_tickers)}")

if not available_tickers:
    st.error("Für keinen Ticker konnten Kursdaten geladen werden.")
    st.stop()

# Sidebar ticker multiselect (nach Datenload)
with st.sidebar:
    active = st.multiselect("Aktive Ticker", options=available_tickers, default=available_tickers[0])

if not active:
    st.info("Bitte mindestens einen aktiven Ticker auswählen.")
    st.stop()

# ---------------- Layout: Big Chart + KPIs/News ----------------
# Viel Platz für den Graphen: 2/3 Breite Chart, 1/3 KPIs/News
left, right = st.columns([2.2, 1.0], gap="large")

with left:
    st.subheader("Kursverlauf (Vergleich)")

    # Option: absolut vs. % Entwicklung
    show_percent = st.toggle("Prozentuale Entwicklung anzeigen", value=True)

    chart_df = pd.DataFrame()

    for t in active:
        df = data.get(t)
        if df is None or df.empty or "Close" not in df.columns:
            continue

        s = df["Close"].dropna().rename(t)
        chart_df = pd.concat([chart_df, s], axis=1)

    if chart_df.empty:
        st.warning("Keine Close-Daten zum Plotten.")
    else:
        # Index sauber ausrichten (gemeinsame Zeitachse)
        
        chart_df = chart_df.sort_index()
        chart_df = chart_df.dropna(how="all")

        if show_percent:
            # Basis je Aktie = erster verfügbarer Wert (nicht zwingend gleiche Kalenderzeile)
            base = chart_df.apply(lambda col: col.dropna().iloc[0] if col.dropna().shape[0] else None)
            chart_pct = (chart_df.divide(base) - 1.0) * 100.0
            chart_pct = chart_pct.dropna(how="all")
            st.line_chart(chart_pct, height=520, use_container_width=True)
        else:
            st.line_chart(chart_df, height=520, use_container_width=True)

    with st.expander("Rohdaten anzeigen"):
        st.dataframe(data[active[0]], use_container_width=True)


with right:
    st.subheader("Kennzahlen")

    t0 = active[0]
    df0 = data[t0]
    info0 = info.get(t0, {}) or {}

    # --- entfernt: lokale fmt-Funktion, wir nutzen fmt aus ui_logic.py ---
    #def fmt(x):
    #    if x is None:
    #        return "n/a"
    #    try:
    #        if isinstance(x, (float, int)):
    #            return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    #        return str(x)
    #    except Exception:
    #        return "n/a"

    close = tu.get_latest_close(df0) if df0 is not None else None
    interval_text = tu.get_interval_text(df0) if df0 is not None else "n/a"

    hi, hi_date = tu.get_high_market_price(df0) if df0 is not None else (None, None)
    lo, lo_date = tu.get_low_market_price(df0) if df0 is not None else (None, None)

    ytd = None
    if df0 is not None and not df0.empty:
        data_year = df0[df0.index.year == datetime.now().year]
        if not data_year.empty:
            start_open = data_year.iloc[0].get("Open", None)
            try:
                if start_open and float(start_open) != 0:
                    ytd = ((float(close) - float(start_open)) / float(start_open)) * 100.0
            except Exception:
                ytd = None

    currency = info0.get("currency", "")

    # Streamlit Metrics
    st.metric("Ticker", info0.get("longName", t0))
    st.metric("Kurs (Close)", f"{fmt(float(close) if close is not None else None)} {currency}".strip())
    st.caption(interval_text)

    st.markdown("---")
    st.write("**Intervall Hoch/Tief**")
    if hi is not None and lo is not None and hi_date is not None and lo_date is not None:
        st.write(f"• Hoch: {fmt(float(hi))} {currency} am {hi_date.strftime('%d.%m.%Y')}")
        st.write(f"• Tief: {fmt(float(lo))} {currency} am {lo_date.strftime('%d.%m.%Y')}")
    else:
        st.write("• n/a")

    st.write("**YTD Performance**")
    st.write("• " + ("n/a" if ytd is None else f"{ytd:.2f} %".replace(".", ",")))

    st.markdown("---")
with right:
    st.subheader("News")
    news_items = news.get(t0, []) or []

    if not news_items:
        st.write("Keine News gefunden.")
    else:
        for item in news_items[:8]:
            item = item["content"]
            title = item.get("title") or "(ohne Titel)"

            # 🔧 FIX: beide Zeitstempel unterstützen
            pub = item.get("providerPublishTime") or item.get("publisherPublishTime")

            when = ""
            if pub:
                try:
                    when = datetime.fromtimestamp(pub).strftime("%d.%m.%Y %H:%M")
                except Exception:
                    when = ""

            # 🔧 FIX: Link aus RSS oder yfinance
            link = item.get("link") or item.get("url") or item.get("canonicalUrl").get("url") or item.get("clickThroughUrl").get("url") or ""

            if link:
                st.markdown(
                    f"• [{title}](<{link}>)"
                    + (f"  \n<span style='color:gray'>{when}</span>" if when else ""),
                    unsafe_allow_html=True,
                )
            else:
                st.write(f"• {title}" + (f" ({when})" if when else ""))

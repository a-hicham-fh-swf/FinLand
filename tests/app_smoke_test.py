import sys
import types


class _SessionState:
    """
    Minimaler Streamlit-SessionState-Ersatz:
    - unterstützt: "key" in st.session_state
    - unterstützt: st.session_state.key = value
    - unterstützt: st.session_state["key"]
    """
    def __init__(self):
        self._data = {}

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, name):
        # Zugriff wie st.session_state.tickers
        if name in self._data:
            return self._data[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == "_data":
            super().__setattr__(name, value)
        else:
            self._data[name] = value


def test_TC_UI_004_app_module_importable_without_starting_streamlit():
    # GIVEN: app.py importiert streamlit und führt beim Import UI-Code aus.
    #        In Unit-Tests wollen wir sicherstellen, dass der Import NICHT crasht.
    #
    #        Damit der Test reproduzierbar ist, stubben wir streamlit minimal:
    #        - alle verwendeten Funktionen existieren
    #        - st.stop() beendet den Import kontrolliert (ohne echten UI-Start)

    fake_st = types.ModuleType("streamlit")

    # Hilfs-Objekt, das als Kontextmanager für "with st.sidebar:" funktioniert
    class _Ctx:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False

    # SessionState-Stub (wichtig für st.session_state.tickers)
    fake_st.session_state = _SessionState()

    # UI-Funktionen, die im app.py beim Import aufgerufen werden können
    fake_st.set_page_config = lambda *a, **k: None
    fake_st.title = lambda *a, **k: None
    fake_st.header = lambda *a, **k: None
    fake_st.subheader = lambda *a, **k: None
    fake_st.markdown = lambda *a, **k: None
    fake_st.caption = lambda *a, **k: None
    fake_st.write = lambda *a, **k: None
    fake_st.warning = lambda *a, **k: None
    fake_st.error = lambda *a, **k: None
    fake_st.info = lambda *a, **k: None
    fake_st.dataframe = lambda *a, **k: None
    fake_st.line_chart = lambda *a, **k: None
    fake_st.metric = lambda *a, **k: None
    fake_st.columns = lambda *a, **k: (_Ctx(), _Ctx())
    fake_st.expander = lambda *a, **k: _Ctx()
    fake_st.spinner = lambda *a, **k: _Ctx()

    # Inputs: wir steuern den Import so, dass app.py früh per st.stop() beendet wird.
    # Dadurch muss der Test nicht das komplette UI "durchlaufen".
    fake_st.selectbox = lambda *a, **k: "3M"
    fake_st.checkbox = lambda *a, **k: False
    fake_st.date_input = lambda *a, **k: __import__("datetime").datetime.now()
    fake_st.multiselect = lambda *a, **k: []
    fake_st.toggle = lambda *a, **k: False

    # stop() beendet kontrolliert (Streamlit stoppt Ausführung im Script)
    fake_st.stop = lambda: (_ for _ in ()).throw(SystemExit())

    # sidebar muss als Context Manager funktionieren
    fake_st.sidebar = _Ctx()

    # streamlit_searchbox ebenfalls stubben (wird importiert)
    fake_searchbox_mod = types.ModuleType("streamlit_searchbox")
    fake_searchbox_mod.st_searchbox = lambda *a, **k: None

    # yfinance stubben, damit data_service importierbar ist (wie bei 4.3 Tests)
    fake_yfinance = types.ModuleType("yfinance")
    fake_yfinance.download = lambda *a, **k: None
    fake_yfinance.Ticker = lambda *a, **k: types.SimpleNamespace(news=[], info={})

    sys.modules["streamlit"] = fake_st
    sys.modules["streamlit_searchbox"] = fake_searchbox_mod
    sys.modules["yfinance"] = fake_yfinance

    # WHEN: app wird importiert
    # THEN: Import soll nicht mit "echtem" Crash abbrechen.
    #      st.stop() löst SystemExit aus – das ist okay und gilt als "kontrolliert beendet".
    try:
        import app  # noqa: F401
    except SystemExit:
        pass

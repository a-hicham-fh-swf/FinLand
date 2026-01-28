import os
import sys
import types
from unittest.mock import MagicMock, patch

import run_app


def test_TC_RUN_001_main_sets_sysargv_opens_browser_and_calls_streamlit_cli():
    # GIVEN:
    # - run_app.main() soll Streamlit "in-process" starten (kein subprocess)
    # - dabei soll:
    #   1) der Browser auf http://localhost:8501 geöffnet werden
    #   2) sys.argv so gesetzt werden, dass Streamlit app.py auf Port 8501 startet
    #   3) streamlit.web.cli.main() aufgerufen werden
    #
    # Für einen Unit-Test darf Streamlit NICHT wirklich starten, daher mocken wir:
    # - webbrowser.open
    # - streamlit.web.cli.main

    # Wir merken uns sys.argv, um es nach dem Test wiederherzustellen
    old_argv = sys.argv[:]

    # Erwarteter Pfad zur app.py (genauso wie in run_app.py berechnet)
    base = os.path.dirname(os.path.abspath(run_app.__file__))
    expected_app_path = os.path.join(base, "app.py")

    # Fake Streamlit CLI Modul: streamlit.web.cli.main()
    fake_cli = types.SimpleNamespace(main=MagicMock(name="streamlit_cli_main"))

    # Wir müssen die Importstelle "from streamlit.web import cli as stcli" abfangen.
    # Das passiert IN main(). Daher legen wir passende Module in sys.modules.
    fake_streamlit = types.ModuleType("streamlit")
    fake_streamlit_web = types.ModuleType("streamlit.web")
    fake_streamlit_web.cli = fake_cli

    sys.modules["streamlit"] = fake_streamlit
    sys.modules["streamlit.web"] = fake_streamlit_web

    try:
        # WHEN: main wird ausgeführt
        with patch("run_app.webbrowser.open") as open_mock:
            run_app.main()

        # THEN:
        # 1) Browser wurde geöffnet
        open_mock.assert_called_once_with("http://localhost:8501")

        # 2) sys.argv ist korrekt gesetzt
        assert sys.argv[0] == "streamlit"
        assert sys.argv[1] == "run"
        assert sys.argv[2] == expected_app_path

        # Flags prüfen (Reihenfolge egal, aber Inhalte müssen enthalten sein)
        argv_str = " ".join(sys.argv)
        assert "--server.port=8501" in argv_str
        assert "--server.headless=true" in argv_str
        assert "--browser.gatherUsageStats=false" in argv_str

        # 3) Streamlit CLI main wurde genau einmal aufgerufen
        fake_cli.main.assert_called_once()

    finally:
        # sys.argv wieder zurücksetzen (Test soll nichts "kaputt" machen)
        sys.argv = old_argv

import os
import sys
import webbrowser

def main():
    # Pfad zur app.py ermitteln
    base = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base, "app.py")

    # Browser öffnen
    webbrowser.open("http://localhost:8501")

    # Streamlit in-process starten (KEIN subprocess!)
    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
    ]

    # Start Streamlit
    stcli.main()

if __name__ == "__main__":
    main()

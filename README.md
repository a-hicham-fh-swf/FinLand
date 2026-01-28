# FinLand – Interaktives Finanzdashboard

## Projektbeschreibung

FinLand ist ein interaktives Finanzdashboard zur Analyse von Aktienkursen, Kennzahlen und Nachrichten.  
Die Anwendung basiert auf Python, Streamlit und externen Finanzdatenquellen und wurde im Rahmen des Mastermoduls „Programmierung für KI“ entwickelt.

---

## Team & Verantwortlichkeiten

| Name | Schwerpunkt | Rolle |
|---|---|---|
| Aït Ayad, Hicham | Backend-Entwicklung (Datenzugriff, Services, Business-Logik) | Product Owner |
| Burgsmüller, Sven | Testing von Utility-Funktionen sowie grundlegender Datenaufbereitung (z. B. Hilfsfunktionen für Kurswerte, Zeiträume) | Scrum Master |
| Calcara, Matthias | Testing von zentraler DataService-Logik, UI-naher Logik, Smoke-Tests, Startpfad der Anwendung | Scrum Master |
| Friedel, Christian | Frontend-Entwicklung (UI, Visualisierung, Nutzerinteraktion) | Product Owner |

Die Testverantwortung wurde bewusst funktional aufgeteilt, nicht nur formal nach Dateien.

---

## Setup

### Python-Version
Getestet mit **Python 3.13.x**.

### Installation

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r src/requirements.txt
```

### macOS Hinweis
Falls die Installation in einer bestehenden/älteren Virtualenv fehlschlägt (z. B. bei `curl_cffi`), 
hilft ein sauberer Neuaufbau der Virtualenv aus dem Projekt-Root:

```bash
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r src/requirements.txt
```

---

## Anwendung starten

```bash
python src/run_app.py
```
Die Anwendung startet lokal über Streamlit
(Standard: http://localhost:8501).

---

## Testing

### Überblick

Das Projekt verwendet pytest für automatisierte Tests.
Die Tests decken sowohl Backend-Logik als auch UI-nahe Logik und Startpfade ab.

### Teststruktur

* tests/data_service_test.py
→ DataService & Datenverarbeitung (Kapitel 4.3)
* tests/ui_logic_test.py
→ UI-Logik (Formatierung, Anzeigeentscheidungen) (Kapitel 4.4)
* tests/app_smoke_test.py
→ Smoke-Test: App-Import ohne Crash (Kapitel 4.4)
* tests/run_app_test.py
→ Entry-Point-Test für run_app.py (Kapitel 4.4)

### Tests ausführen

```bash
python -m pytest
```

## Hinweise zur Implementierung (Testing 4.3 & 4.4)

Für eine saubere und testbare Architektur wurde im Rahmen der Tests:
* die UI-Logik bewusst aus app.py ausgelagert nach src/ui_logic.py
(reine, testbare Funktionen),
* in app.py lediglich die lokale fmt()-Funktion entfernt und durch den Import aus ui_logic.py ersetzt,
* externe Abhängigkeiten (z. B. yfinance, streamlit) in Tests konsequent gemockt,
um reproduzierbare Unit-Tests zu ermöglichen.

Die funktionale Logik der Anwendung wurde dabei nicht verändert, sondern lediglich testbar gemacht.

---

## Abhängigkeiten / requirements.txt

Die finale requirements.txt wurde gemäß Vorgabe des Dozenten am Ende per pip freeze erzeugt.

---

## Quellen & KI-Unterstützung

### KI-Unterstützung

OpenAI ChatGPT wurde zur Unterstützung bei:
* Konzeption und Implementierung von pytest-Tests
* Testarchitektur (Mocking, Isolation, Smoke-Tests)
* Strukturierung der technischen Dokumentation
eingesetzt.

### Fachliche Quellen

* Offizielle Dokumentationen von pytest, pandas und Streamlit
* Python-Standardbibliothek (unittest.mock, sys, os)

Die KI-Unterstützung diente ausschließlich als Hilfsmittel;
Verständnis, Integration und Abnahme der Ergebnisse erfolgten eigenständig.

---

## Aktueller Status (Repo-Stand)

* Gesamter Testlauf (python -m pytest): 60/60 Tests erfolgreich
* Testanteil (DataService, UI-Logik, Smoke- & Starttests): 17/17 Tests, vollständig grün
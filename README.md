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

## Hinweise zur Implementierung

### Gesamtziel der Implementierung

Die Implementierung des Projekts FinLand verfolgt das Ziel, eine klar strukturierte, wartbare und nachvollziehbare Anwendung zu schaffen.  
Dabei wurde Wert gelegt auf:

- eine verständliche Modulstruktur,
- eine klare Datenfluss-Logik,
- eine gute Erweiter- und Testbarkeit,
- sowie eine saubere Trennung von Schwerpunkten.

Die folgenden Hinweise beschreiben die Implementierung projektweit und gelten unabhängig von einzelnen Team- oder Testanteilen.

---

### Projektstruktur und Modulaufteilung

Das Projekt ist in zwei zentrale Bereiche gegliedert:

- **`src/`**  
  Enthält den vollständigen Produktivcode der Anwendung.

- **`tests/`**  
  Enthält alle automatisierten Tests (Unit- und Smoke-Tests).

Diese Trennung folgt gängigen Python-Konventionen und sorgt für Übersichtlichkeit sowie eine klare Abgrenzung zwischen Anwendungscode und Testcode.

---

### Zentrale Module und ihre Aufgaben

Im Folgenden sind die zentralen Module des Projekts einzeln aufgeführt, damit die Struktur des Repositories direkt nachvollziehbar ist.

- **`src/run_app.py` (Startskript / Entry Point)**  
  Startet die Streamlit-Anwendung.  
  Aufgaben:
  - kapselt den Startprozess (Streamlit-CLI-Aufruf),
  - definiert einen klaren Einstiegspunkt,
  - ermöglicht Smoke-Tests des Startpfads ohne echten UI-Start.

- **`src/app.py` (Streamlit UI / Orchestrierung)**  
  Hauptanwendung auf Basis von Streamlit.  
  Aufgaben:
  - UI-Layout und Nutzerinteraktion (Sidebar, Auswahl, Darstellung),
  - Orchestrierung der Datenabfrage über Service-/Logikmodule,
  - Anzeige von Charts, Kennzahlen und News.

- **`src/data_service.py` (Service-Schicht / Datenzugriff)**  
  Kapselt den Zugriff auf Finanzdaten (z. B. über `yfinance`) und bereitet diese für die UI auf.  
  Aufgaben:
  - Abruf von Kursdaten (Perioden / Datumsspannen),
  - Normalisierung der Datenstruktur,
  - Caching/TTL (zur Performance und Reproduzierbarkeit),
  - Abruf von Zusatzinformationen (Info/News) inkl. Fallback-Logik.

- **`src/ticker_utils.py` (Fachliche Hilfsfunktionen)**  
  Enthält Hilfsfunktionen zur Auswertung von Kursdaten.  
  Aufgaben:
  - Extraktion von Kennwerten (z. B. letzter Close),
  - High/Low-Logik inkl. Datum,
  - Zeitintervall-/Datumslogik (Start/Ende, Intervalltext, Periodenlogik).

- **`src/ui_logic.py` (UI-nahe Logik ohne Streamlit-Abhängigkeit)**  
  Enthält Logik, die für die Darstellung relevant ist, aber unabhängig von Streamlit getestet werden kann.  
  Aufgaben:
  - Formatierung von Zahlen- und Prozentwerten,
  - Anzeigeentscheidungen (z. B. ob ein Chart sinnvoll ist).

- **`src/utils.py` (Allgemeine Utilities / Cache & Singleton)**  
  Enthält allgemeine Hilfsstrukturen, die modulübergreifend genutzt werden.  
  Aufgaben:
  - Singleton-Implementierung (`Singleton`),
  - Ticker-Cache mit TTL-Logik (`TickerCache`) und Cache-Verwaltung.

- **`src/main_app.py` (CLI/Console-Variante)**  
  Konsolenbasierte Variante zur Abfrage/Analyse von Tickern (Eingabe über Terminal).  
  Aufgaben:
  - Start über `__main__` und `input()`-Dialog,
  - Abruf von Kursdaten über `yfinance` (inkl. Periodenlogik),
  - Ausgabe von Kennzahlen (aktueller Close, High/Low, YTD-Performance),
  - nutzt `utils.Singleton`, `utils.TickerCache` sowie `ticker_utils`.

---

### Kategorisierung (zusätzliche Einordnung)

- **Start / Entry Point:** `run_app.py` (Streamlit), `main_app.py` (CLI)
- **UI / Orchestrierung:** `app.py`
- **Service / Datenzugriff:** `data_service.py`
- **Logik & Utilities:** `ticker_utils.py`, `ui_logic.py`, `utils.py`

---

### Datenfluss innerhalb der Anwendung

Der Datenfluss ist bewusst linear und nachvollziehbar aufgebaut:

1. Der Nutzer interagiert über die Benutzeroberfläche (`app.py`).
2. Die Anwendung fordert Daten über Service-Module an.
3. Die Daten werden verarbeitet, normalisiert und geprüft.
4. UI-nahe Logik entscheidet über Darstellung und Format.
5. Ergebnisse werden in der Benutzeroberfläche angezeigt.

Durch diese Struktur lassen sich Datenverarbeitung, Darstellung und Steuerung klar voneinander trennen.

---

### Trennung von UI, Logik und Datenverarbeitung

Ein zentrales Implementierungsprinzip ist die Trennung von:

- **UI-Code** (Darstellung, Nutzerinteraktion),
- **Logik-Code** (Entscheidungen, Berechnungen, Formatierung),
- **Datenverarbeitung** (Abruf, Normalisierung, Validierung).

Diese Trennung:
- erhöht die Lesbarkeit des Codes,
- erleichtert Erweiterungen,
- reduziert Seiteneffekte,
- und ermöglicht gezieltes Testen einzelner Komponenten.

---

### Umgang mit externen Abhängigkeiten

Externe Bibliotheken und Dienste (z. B. Finanzdatenquellen oder UI-Frameworks) werden im Produktivcode gezielt eingesetzt, im Testkontext jedoch isoliert behandelt.

In der Implementierung wurde darauf geachtet:
- externe Abhängigkeiten klar zu kapseln,
- ihre Nutzung auf definierte Stellen zu beschränken,
- und keine unnötigen Abhängigkeiten zwischen Modulen zu erzeugen.

---

### Testbarkeit als Qualitätsaspekt

Testbarkeit ist kein Selbstzweck, sondern ein Qualitätsmerkmal der Implementierung.

Die Struktur des Codes ermöglicht:
- das isolierte Testen einzelner Module,
- das Importieren zentraler Komponenten ohne Seiteneffekte,
- sowie automatisierte Tests ohne echte externe Aufrufe.

Testrelevante Anpassungen (z. B. Auslagerung von Logik aus der UI) wurden so vorgenommen, dass die fachliche Funktionalität der Anwendung nicht verändert, sondern lediglich besser überprüfbar gemacht wurde.

---

### Abgrenzung von Schwerpunkten

Die Implementierung ist so gestaltet, dass:
- einzelne Module klar abgegrenzte Aufgaben besitzen,
- Änderungen lokal vorgenommen werden können,
- und Schwerpunkte im Team eindeutig zuordenbar bleiben.

---

### Zusammenfassung

Die Implementierung von FinLand folgt klaren strukturellen Prinzipien:

- modulare Architektur,
- klare Trennung von Zuständigkeiten,
- nachvollziehbarer Datenfluss,
- kontrollierter Startmechanismus,
- und integrierte, aber nicht dominante Berücksichtigung der Testbarkeit.

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
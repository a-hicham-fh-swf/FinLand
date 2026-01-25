# FinLand – Finanzdashboard

## Setup

### Python Version
Getestet mit **Python 3.13.x**.

### Installation
```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r src/requirements.txt

### macOS Hinweis
Falls die Installation in einer bestehenden/älteren Virtualenv fehlschlägt (z. B. bei `curl_cffi`), 
hilft ein sauberer Neuaufbau der Virtualenv aus dem Projekt-Root:

```bash
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r src/requirements.txt

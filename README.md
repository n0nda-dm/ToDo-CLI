# 📝 ToDo-CLI
Eine einfache, farbenfrohe Kommandozeilen-Aufgabenverwaltung geschrieben in Python mit Typer und Rich.


## ✨ Features
- Einfache Verwaltung von Aufgaben über die Kommandozeilen
- 🎨 Farbige Ausgabe mit automatischer Deadline-Warnung
    - 🔴 Rot = Deadline überschritten
    - 🟡 Gelb = Weniger als 24 Stunden
    - 🟢 Grün = Noch Zeit
- Übersichtliche Tabellen dank Rich-Library
- Automatische Trennung von aktiven und abgeschlossenen Aufgaben
- ⚙️ Konfigurierbarer Speicherort
- 🔢 Prioritätssystem (low, medium, high, urgent)
- 📆 Optionale Deadlines mit Datum und Uhrzeit

---
---
--- 

## Installation
### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Insaller)

### Für Endbenutzer (Einfache Installation)
```bash
# 1. Repository klonen
git clone https://github.com/n0nda-dm/ToDo-CLI.git
cd todo-cli

# 2. Virtual Environment erstellen (empfohlen)
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# ODER: venv/Scripts/activate   # Windows

# 3. Installieren
pip install -e .

# 4. Fertig! Jetzt kannst du 'todo' überall nutzen
todo --help
```

### Alternative: Ohne Git
```bash
# 1. Lade das Repository als ZIP herunter
# 2. Entpacke es
# 3. Terminal im entpackten Ordner öffnen

# 4. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 5. Installieren
pip install -e .
```

---
---
---

## Verwendung

### Schnellstart
```bash
# Erste ToDo erstellen
todo create "Einkaufen"

# Alle ToDos anzeigen
todo list

# Details anzeigen
todo show 1

# Als erledigt markieren
todo update 1 --finished
```

### Alle Befehle
#### 📝 Neue ToDo erstellen
```bash
# Minimal
todo create "Aufgabe"

# Mit allen Optionen
todo create "Arzttermin" \
--description "Zahnarzt Dr. Müller" \
--priority urgent \
--deadline "15.02.2026-14:30"
```
#### Optionen:
- -d, --description TEXT - Beschreibung der Aufgabe
- -p, --priority [low|medium|high|urgent] - Priorität (Standard: medium)
- --deadline TEXT - Deadline im Format dd.mm.yyyy-HH:MM


#### 📋 ToDos auflisten
```bash
# Nur aktive Aufgaben
todo list

# Alle (aktive + abgeschlossene)
todo list --all

# Nur abgeschlossene
todo list --finished
```


#### 🔍 Details anzeigen
```bash
todo show <ID>

# Beispiel:
todo show 5
```
##### Zeigt:
- Titel
- Beschreibung
- Priorität
- Status
- Deadline (mit Farbwarnung!)
- Erstellungsdatum
- Abschlussdatum (falls erledigt)


#### ✏️ ToDo bearbeiten
```bash
# Titel ändern
todo update <ID> --title "Neuer Titel"

# Beschreibung ändern
todo update <ID> --description "Neue Beschreibung"

# Priorität ändern
todo update <ID> --priority high

# Als erledigt markieren (verschiebt automatisch)
todo update <ID> --finished

# Mehrere Änderungen gleichzeitig
todo update <ID> --title "Neuer Titel" --priority urgent --finished
```


#### 🗑️ ToDo löschen
```bash
# Mit Bestätigung
todo delete <ID>

# Ohne Bestätigung
todo delete <ID> --force
```


#### ⚙️ Konfiguration
```bash
# Aktuelle Einstellungen anzeigen
todo config --show

# Speicherort ändern
todo config --set-dir /pfad/zu/deinem/ordner

Beispiele:
todo config --set-dir ~/Dokumente/meine-todos
todo config --set-dir /run/media/user/USB/todos
```

---
---
--- 

## 📁 Ordner-Struktur
Nach der Installation erstellt ToDo-CLI automatisch folgende Struktur:
```
~/todos/                   (Standard, anpassbar mit config)
├── working/
│   ├── 1.json             (Aktive Aufgaben)
│   ├── 2.json
│   └── 3.json
└── finished/
    ├── 4.json             (Erledigte Aufgaben)
    └── 5.json
```
Jede ToDo wird als separate JSON-Datei gespeichert.

---
---
--- 

## 🔢 Prioritäten

| Priorität | Beschreibung | Verwendung |
|----------|----------|----------|
| low  | Niedrig   | Kann warten   |
| medium  | Mittel   | Standard-Priorität   |
| high  | Hoch   | Wichtig   |
| urgent  | Dringend   | Sofort erledigen!   |

---
---
--- 

## 📆 Deadline

### Deadline-Format
dd.mm.yyyy-HH:MM

#### Beispiele:
- 15.02.2026-14:30 -> 15. Februar 2026, 14:30 Uhr
- 31.12.2026-23:59 -> 31. Dezember 2026, 23:59 Uhr

### Deadline-Farben:
- 🔴 Rot - Deadline ist überschritten
- 🟡 Gelb - Weniger als 24 Stunden verbleibend
- 🟢 Grün - Noch mehr als 24 Stunden Zeit

---
---
--- 

## 🛠️ Für Entwickler

### Entwicklungsumgebung einrichten
```bash
# Repository klonen
git clone https://github.com/n0nda-dm/ToDo-CLI.git
cd todo-cli

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -e .

# Entwickeln!
# Änderungen in todo.py wirken sofort (editable install)
```

### Projekt-Struktur
```
todo-cli/
├── todo.py              # Hauptprogramm
├── pyproject.toml       # Projekt-Konfiguration
├── README.md            # Diese Datei
├── .gitignore           # Git-Ignore
└── venv/                # Virtual Environment (nicht im Git)
```

### Abhängigkeiten
- typer - CLI-Framework
- rich - Terminal-Formatierung und Farben
- Python 3.8+ - Basis

---
---
--- 

## Beispiel-Workflow
```bash
# 1. Neue Aufgabe hinzufügen
todo create "Python lernen" \
  --description "Typer und Click verstehen" \
  --priority high \
  --deadline "2026.02.10-18:00"

# 2. Liste anschauen
todo list

# Ausgabe
# ┏━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓
# ┃ ID ┃ Titel         ┃ Priorität┃ Status  ┃ Deadline          ┃
# ┡━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩
# │  1 │ Python lernen │ high     │ working │ 2026.02.10 - 18:00│
# └────┴───────────────┴──────────┴─────────┴───────────────────┘

# 3. Details anzeigen
todo show 1

# 4. Später: Als erledigt markieren
todo update 1 --finished

# 5. Abgeschlossene Aufgaben anzeigen
todo list --finished
```

---
---
--- 

## ❗ Häufige Probleme

todo: command not found
### Lösung:
```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Projekt neu installieren
pip install -e .
```

No module named 'typer'
### Lösung:
```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies installieren
pip install typer rich
```

Ordner wird nicht gefunden
### Lösung:
```bash
# Prüfe aktuelle Konfiguration
todo config --show

# Setzte neuen Ordner
todo config --set-dir ~/todos
```

---
---
--- 

## 📚 Quellen & Lernen

Dieses Projekt entstand als Lernprojekt zum Verstehen von CLI-Entwicklung in Python.

Verwendete Ressourcen:
- Typer Documentation (https://typer.tiangolo.com)
- Rich Documentation (https://rich.readthedocs.io/en/stable/)
- YouTube: "Build a Real Python CLI with Click" von ArjanCodes
- Claude (Anthropic): Unterstützung bei Code-Struktur und Erklärungen
- Stack Overflow, Reddit & W3Schools: Verschiedene Python- und CLI-Fragen, sowie Erklärungen 

---
---
--- 

## Lernziele
- Typer CLI-Framework verstehen
- Datei-Management mit pathlib
- JSON-Serialisierung und Deserialisierung
- Rich Terminal-Formatierung
- Datetime-Handling in Python

---
---
--- 

## Mögliche zukünftige Features
Ideen für mögliche Erweiterungen (keine Garantie):

- Tags/Kategorien - Aufgaben nach Themen gruppieren
- Recurring Tasks - Wiederkehrende Aufgaben automatisch erstellen
- Export Funktion - Liste als CSV exportieren

Weitere Vorschläge sind willkommen!

---
---
--- 

## Status
Version: 1.0.0

Alle Grundfunktionen sind implementiert und getestet. Das Projekt ist voll funktionsfähig.

---
---
--- 

## Lizenz
Dieses Projekt ist frei verfügbar für persönliche und Lernzwecke.

---
---
--- 

## 🤝🏻 Feedback
Dieses Projekt entstand als Lernprojekt.

Willkommen sind:
- Bug-Reports - Fehler via GitHub Issues melden
- Feature-Vorschläge - Ideen für Verbesserungen
- Konstruktives Feedback

Hinweis: 
    Code-Beiträge (Pull Requests) nehme ich aktuell nicht an, da ich das Projekt selbst als Lernübung entwickeln möchte. 
    Danke für dein Verständnis!

---
---
--- 

## 👤 Autor
Erstellt als Lernprojekt zur Vertiefung meiner Python-Kenntnisse.

Ziel:
    Von Spielen zu produktivem Programmieren wechseln und CLI-Entwicklung meistern!

---
---
--- 

Viel Erfolg beim Organisieren deiner Aufgaben! 📝✨
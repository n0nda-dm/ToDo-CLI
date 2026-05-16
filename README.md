# 📝 ToDo-CLI
Eine einfache, farbenfrohe Kommandozeilen-Aufgabenverwaltung geschrieben in Python mit Typer und Rich.


## ✨ Features
- Einfache Verwaltung von Aufgaben über die Kommandozeilen
- 🎨 Farbige Ausgabe mit automatischer Deadline-Warnung
    - 🔴 Rot = Deadline überschritten
    - 🟡 Gelb = Weniger als 24 Stunden
    - 🟢 Grün = Noch Zeit
    - 🔵 Cyan = Für aktuellen Zeitraum abgeschlossen (completed)
    - ⚪ Grau(dim) = Endgültig abgeschlossen (finished)
- Übersichtliche Tabellen dank Rich-Library
- Automatische Trennung von aktiven und abgeschlossenen Aufgaben
- ⚙️ Konfigurierbarer Speicherort
- 🔢 Prioritätssystem (low, medium, high, urgent)
- 📆 Optionale Deadlines mit Datum und Uhrzeit

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
--category "Gesundheit" \
--tags "Arzt, Zähne" \
--priority "high" \
--start "15.02.2026-08:30" \
--deadline "15.02.2026-14:30" \
--repeat "w" \
--every 4
```
##### Optionen:
- --description TEXT - Beschreibung der Aufgabe
- --category TEXT - Kategorie der Aufgabe
- --tags TEXT - Tags der Aufgabe
- -p, --priority [low|medium|high|urgent] - Priorität (Standard: medium)
- -s, --start TEXT Start-Time im Format: dd.mm.yyyy-HH:MM
- -d, --deadline TEXT - Deadline im Format: dd.mm.yyyy-HH:MM
- -r, --repeat [d|w|m|y] - Wiederholung (Standard: None)
- -e, --every INTEGER - Anpassungen der Wiederholungen (z.B.: -r m -e 4 = Wiederholung findet nicht monatlich, sondern alle 4 Monate statt)

> **Hinweis:** `--category` und `--tags` haben bei `todo create` absichtlich keine Kurzflags,
> da `-c` und `-t` bei `todo update` bereits für `--completed` und `--title` vergeben sind.

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
- Start-Time (mit Farbwarnung!)
- Deadline (mit Farbwarnung!)
- Dauer in Stunden (solange Start und Deadline gegeben sind)
- Erstellungsdatum
- Abschlusshistorie (solange ein Datum bereits enthalten ist)
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
##### Optionen:
- -t, --title TEXT - Neuer Titel
- --description TEXT - Beschreibung der Aufgabe
- --category TEXT - Kategorie der Aufgabe
- --tags TEXT - Tags der Aufgabe
- -p, --priority [low|medium|high|urgent] - Priorität (Standard: medium)
- -s, --start TEXT Start-Time im Format: dd.mm.yyyy-HH:MM
- -d, --deadline TEXT - Deadline im Format: dd.mm.yyyy-HH:MM
- -r, --repeat [d|w|m|y] - Wiederholung (Standard: None)
- -e, --every INTEGER - Anpassungen der Wiederholungen (z.B.: -r m -e 4 = Wiederholung findet nicht monatlich, sondern alle 4 Monate statt)
- -c, --completed BOOL - Eine sich wiederholende ToDo für die momentane Deadline als abgeschlossen markieren
- -f, --finished BOOL - Eine ToDo endgültig abschließen 

#### 🗑️ ToDo löschen
```bash
# Mit Bestätigung
todo delete <ID>

# Ohne Bestätigung
todo delete <ID> --force
```

#### Migration 
```bash
# Alle ToDos aktualisieren (falls es neue Variablen/Werte gibt)
todo migrate
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

| Priorität | Beschreibung | Verwendung         |
|-----------|--------------|--------------------|
| low       | Niedrig      | Kann warten        |
| medium    | Mittel       | Standard-Priorität |
| high      | Hoch         | Wichtig            |
| urgent    | Dringend     | Sofort erledigen!  |

--- 

## 📆 Start-Time und Deadline

### Format
dd.mm.yyyy-HH:MM

#### Beispiele:
- 2026.02.15-08:30 -> 15. Februar 2026, 08:30 Uhr
- 15.02.2026-14:30 -> 15. Februar 2026, 14:30 Uhr
- 31.12.2026-23:59 -> 31. Dezember 2026, 23:59 Uhr

### Farben:
- 🔴 Rot - Deadline ist überschritten
- 🟡 Gelb - Weniger als 24 Stunden verbleibend
- 🟢 Grün - Noch mehr als 24 Stunden Zeit

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

## 📚 Quellen & Lernen

Dieses Projekt entstand als Lernprojekt zum Verstehen von CLI-Entwicklung in Python.

Verwendete Ressourcen:
- Typer Documentation (https://typer.tiangolo.com)
- Rich Documentation (https://rich.readthedocs.io/en/stable/)
- YouTube: "Build a Real Python CLI with Click" von ArjanCodes
- Claude (Anthropic): Unterstützung bei Code-Struktur und Erklärungen
- Stack Overflow, Reddit & W3Schools: Verschiedene Python- und CLI-Fragen, sowie Erklärungen 

--- 

## Lernziele
- Typer CLI-Framework verstehen
- Datei-Management mit pathlib
- JSON-Serialisierung und Deserialisierung
- Rich Terminal-Formatierung
- Datetime-Handling in Python

--- 

## Mögliche zukünftige Features
Ideen für mögliche Erweiterungen (keine Garantie):

- Export Funktion - Liste als CSV exportieren

Weitere Vorschläge sind willkommen!

--- 

## Changelog

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert.

> **Versionshistorie**: Bis Version 1.0.0 wurde das Projekt als `0.1.0` entwickelt.

---

### [1.2.0] - 2026-05-16

#### Added
- Kategorie: ToDos können nun eine Kategorie haben, z.B. --category "Geschäftlich"
- Tags: ToDos können nun auch Tags haben, z.B. --tags "dev, Python, coding, CLI-Tool"

#### Changed
- todo list: Zeigt nun nicht mehr Status an, hierfür aber Kategorie und Tags
- get_datetime_color(): Nun haben auch completed ToDos eine eigene Farbe, sodass der Status bei "todo list" nicht mehr benötigt wird

#### Migration (fuer bestehende Nutzer)
Solltet ihr euer Tool updaten, müsst ihr erstmal "todo migrate" ausführen.

---

### [1.1.2] - 2026-05-03

#### Fixed
- ToDos mit Status "completed" wurden zu früh reaktiviert
- Deadlines wurden nicht korrekt bei wiederkehrenden Aufgaben aktualisiert

#### Changed
- Refactored: `check_and_reactivate_todo()` und `update_datetime()` zusammengelegt zu `check_and_update_todo()`

#### Migration (für bestehende Nutzer)
Falls eine ToDo nach dem Update falsch berechnet wird:
1. Öffne die `.json` Datei im ToDo-Verzeichnis (z.B. `26.json`)
2. Setze `start_time` und `deadline` auf die aktuellen Werte
3. Setze `occurrence_count` auf die richtige Anzahl (z.B. `1` für die erste Wiederholung nach Original)
4. Beim nächsten `todo list` wird es korrekt berechnet

**Beispiel:**
```json
{
    "start_time": "2026-05-01T08:00:00",            //Aktueller Zeitraun
    "deadline": "2026-05-03T20:00:00",              //Aktueller Zeitraun
    "original_start_time": "2026-04-01T08:00:00",   //Erster Zeitraum
    "original_deadline": "2026-04-03T20:00:00",     //Erster Zeitraum
    "occurrence_count": 1,                          //Anzahl Wiederholungen
}
```

---

### [1.1.1] - 2026-04-13

#### Fixed
- Sortierung bei `todo list` nutzte veraltete Zeiten statt aktuelle Zeitspanne

#### Changed
- Farbcodierung für Zeiten: Abgeschlossene ToDos zeigen nicht mehr rot (bessere Unterscheidung bei `todo list -a`)

---

### [1.1.0] - 2026-04-01

#### Added
- **Start-Zeit**: ToDos können jetzt eine Start-Zeit haben (von-bis statt nur bis)
- **Completion History**: Wiederholende ToDos können als "completed" markiert werden
    - Wird ausgeblendet bis Zeitraum vorbei ist
    - Historie zeigt alle Abschlüsse in `todo show`

#### Changed
- **Wiederholungs-Anzeige**: Zeigt jetzt "jede 4. Woche" statt nur "wöchentlich"

---

### [1.0.0] - 2026-02-13

Erste stabile Version!

#### Features
- Erstellen, Bearbeiten, Löschen von ToDos
- Prioritäten (low, medium, high, urgent)
- Deadlines mit Farbcodierung
- Wiederholende Aufgaben (täglich, wöchentlich, monatlich, jährlich)
- Status-Verwaltung (working, finished)
- Rich CLI mit farbiger Ausgabe

> **Hinweis**: Diese Version wurde ursprünglich als `0.1.0` released

--- 

## Lizenz
Dieses Projekt ist frei verfügbar für persönliche und Lernzwecke.

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

## 👤 Autor
Erstellt als Lernprojekt zur Vertiefung meiner Python-Kenntnisse.

Ziel:
    Von Spielen zu produktivem Programmieren wechseln und CLI-Entwicklung meistern!

--- 

Viel Erfolg beim Organisieren deiner Aufgaben! 📝✨
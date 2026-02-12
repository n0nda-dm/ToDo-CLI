# Entwickler-Notizen (nur für mich)
Diese Datei enthält meine persönlichen Notizen zum Projekt.
Nicht auf GitHub hochladen! (steht in .gitignore)

---

## Was ich gelernt habe:

### Pythen-Konzepte
- Virtual Environment (venv)
- Type Hints (-> None, -> str)
- Decorator (@app.command())
- Context Managers (with open())
- Try-Except Error Handling
- Pathlib für Dateipfade
- JSON Serialisierung/Deserialisierung

### Typer-Konzepte:
- CLI-Framework Grundlagen
- Arguments vs. Options
- Automatische --help Generierung

### Best Practices
- Trennung von Funktionen (Single Responsibility)
- Config-Dateien für Benutzer-Einstellungen
- Ordner-Strukturierung (working/finished)
- Error Handling mit aussagekräftigen Meldungen

---

## Bekannte Bugs / TODOs

### Kritisch:
- Keine Tests vorhanden (später hinzufügen)
- Keine Validierung bei deadline-Format (teilweise implementiert)

### Nice-to-have:
- Farben für Titel in list und show
- Bessere Formatierung bei show (untereinander)
- Suche nach Titel/Beschreibung
- Filter nach Priorität
- Export-Funktion (CSV/JSON)

---

## Farb-Codes (Rich)
```python
# Basis-Farben:
"red", "green", "blue", "yellow", "cyan", "magenta", "white"

# Modifikatoren:
"bold", "dim", "italic", "underline"

# Kombiniert:
"[bold red]Text[/bold red]"
"[dim cyan]Text[/dim cyan]"

# Meine Verwendung:
- Deadlines: red/yellow/green (je nach Zeit)
- Titel: cyan (geplant)
- Status: green (working), dim (finished)
```

---

## Ordner-Struktur-Erklärung
```
~/.config/todo-cli/
└── config.json           # Speichert: wo todos liegen

~/todos/                  # Standard (kann geändert werden)
├── working/
│   ├── 1.json
│   └── 2.json
└── finished/
    └── 5.json

/run/media/.../ToDo-CLI/  # Entwicklungsordner
├── venv/                 # Virtual Environment
├── todo.py               # Hauptcode
├── pyproject.toml        # Projekt-Config
├── README.md             # Für andere User
├── DEVNOTES.md           # Diese Datei (NUR FÜR MICH!)
└── .gitignore
```

---

## Workflow für Änderungen
```bash
# 1. Code ändern in VSCode
# 2. Testen:
todo create "Test"

# 3. Wenn gut -> Git:
git add .
git commit -m "Feature: XYZ hinzugefügt"
git push

# Fertig!
```

---

## Wichtige Links (für später):
- Typer Docs https://typer.tiangolo.com/
- Rich Docs https://rich.readthedocs.io/
- Python pathlib https://docs.python.org/3/library/pathlib.html
- Python datetime https://docs.python.org/3/library/datetime.html
- Git Cheatsheet https://education.github.com/git-cheat-sheet-education.pdf
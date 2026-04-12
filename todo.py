#!/usr/bin/env python3
"""
ToDo-CLI – Eine einfache Aufgabenverwaltung für die Kommandozeile
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from pathlib import Path
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Typer App initialisieren
app = typer.Typer(help="📝 ToDo-CLI - Verwalte deine Aufgaben")
console = Console()

# Globale Konfiguration
CONFIG_FILE = Path.home() / ".config" / "todo-cli" / "config.json"
DEFAULT_TODO_DIR = Path.home() / "todos"


def get_config() -> dict:
    """Lade die Konfiguration oder erstelle Standardkonfiguration"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"todo_dir": str(DEFAULT_TODO_DIR)}


def save_config(config: dict):
    """Speichere die Konfiguration"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def get_todo_dir() -> Path:
    """Hole das ToDo-Verzeichnis aus der Config"""
    config = get_config()
    return Path(config["todo_dir"])


def ensure_directories():
    """Stelle sicher, dass die benötigten Ordner existieren"""
    todo_dir = get_todo_dir()
    (todo_dir / "working").mkdir(parents=True, exist_ok=True)
    (todo_dir / "finished").mkdir(parents=True, exist_ok=True)


def get_next_id() -> int:
    """Ermittle die nächste freie ID"""
    import os

    # sicher stellen: Ordner existieren
    ensure_directories()
    todo_dir = get_todo_dir()

    # Neuer Versuch: os.listdir (da es mit .glob() usw. nur Probleme gab...)
    working_files: list[Path] = []
    finished_files: list[Path] = []

    try:
        working_path = todo_dir / "working"
        if working_path.exists():
            files = os.listdir(working_path)
            working_files = [working_path / f for f in files if f.endswith('.json')]
    except Exception as e:
        console.print(f"[yellow]Warnung: Fehler beim Lesen von working/: {e}[/yellow]")

    try:
        finished_path = todo_dir / "finished"
        if finished_path.exists():
            files = os.listdir(finished_path)
            finished_files = [finished_path / f for f in files if f.endswith('.json')]
    except Exception as e:
        console.print(f"[yellow]Warnung: Fehler beim Lesen von finished/: {e}[/yellow]")
    
    # Sammeln aller IDs
    all_ids: list[int] = []
    all_files: list[Path] = working_files + finished_files

    for todo_file in all_files:
        try:
            # Extrahieren der ID aus Dateinamen (ohne .json)
            file_id = int(todo_file.stem)
            all_ids.append(file_id)
        except (ValueError, AttributeError):
            continue

    # Keine IDs gefunden
    if not all_ids:
        return 1

    return max(all_ids) + 1


def load_todo(todo_id: int) -> tuple[Optional[dict], Optional[Path]]:
    """Lade eine ToDo anhand ihrer ID
    
    Returns:
        tuple: (todo_data, file_path) oder (None, None) wenn nicht gefunden
    """
    todo_dir = get_todo_dir()
    
    # Suche in working/
    working_file = todo_dir / "working" / f"{todo_id}.json"
    if working_file.exists():
        with open(working_file, "r") as f:
            todo_data = json.load(f)

        # Stille Migration
        todo_data = migrate_todo_data(todo_data)

        return todo_data, working_file
    
    # Suche in finished/
    finished_file = todo_dir / "finished" / f"{todo_id}.json"
    if finished_file.exists():
        with open(finished_file, "r") as f:
            todo_data = json.load(f)

        # Stille Migration
        todo_data = migrate_todo_data(todo_data)

        return todo_data, finished_file
    
    return None, None


def save_todo(todo_data: dict, status: str = "working"):
    """Speichere eine ToDo"""
    ensure_directories()
    todo_dir = get_todo_dir()
    filename = f"{todo_data["id"]}.json"
    if todo_data["status"] == "finished":
        filepath = todo_dir / status / filename
    else:
        filepath = todo_dir / "working" / filename
    # filepath = todo_dir / status / filename
    
    with open(filepath, "w") as f:
        json.dump(todo_data, f, indent=4)


def get_todo_schema() -> dict:
    """Definiert das vollständige ToDo-Schema mit Standardwerten
    
    Alle neuen Felder hier hinzufügen -> Migration erfolgt automatisch
    """
    return {
        # PFLICHTFELDER (werden nicht überschrieben)
        "id": None,
        "title": None, 
        "created_at": None,
        # Optionale Felder (mit Standardwerten)
        "description": None,
        "priority": "medium",
        "status": "working",
        "start_time": None,
        "original_start_time": None,
        "deadline": None,
        "original_deadline": None,
        "duration_hours": None,
        "repeat": None,
        "repeat_every": None,
        "occurrence_count": 0,
        "completion_history": [],
        "finished_at": None
    }


def migrate_todo_data(todo: dict) -> dict:
    """Migriere ToDo auf aktuelles Schema
    
    Fügt alle fehlenden Felder aus dem Schema (get_todo_schema()) hinzu.
    Überschreibt keine existierenden Werte (außer in Spezialfällen)
    """
    schema = get_todo_schema()

    # Hinzufügen der fehlenden Felder
    for field, default_value in schema.items():
        if field not in todo:
            # Spezialfall: repeat_every nur setzen wenn repeat existiert
            if field == "repeat_every":
                if todo.get("repeat") is not None:
                    todo[field] = 1
                else:
                    todo[field] = None
            else:
                todo[field] = default_value

    # Spezialfall: duration_hours berechnen wenn möglich
    if todo.get("duration_hours") is None:
        try:
            if todo.get("start_time") is not None and todo.get("deadline") is not None:
                start = datetime.fromisoformat(todo["start_time"])
                end = datetime.fromisoformat(todo["deadline"])
                diff = end - start
                todo["duration_hours"] = round(diff.total_seconds() / 3600, 2)
        except (ValueError, TypeError):
            pass
    
    return todo


def format_repeat(rp_string: Optional[str], every: Optional[int]) -> str:
    """Formatiere Repeat-String für Anzeige"""
    if not rp_string:
        return "-"
    
    if every == 1:
        if rp_string == "d":
            return "täglich"
        elif rp_string == "w":
            return "wöchentlich"
        elif rp_string == "m":
            return "monatlich"
        elif rp_string == "y":
            return "jährlich"
        elif rp_string is None:
            return "-"
        else:
            return rp_string
    else:
        if rp_string == "d":
            return f"jeden {every}. Tag"
        elif rp_string == "w":
            return f"jede {every}. Woche"
        elif rp_string == "m":
            return f"jeden {every}. Monat"
        elif rp_string == "y":
            return f"jedes {every}. Jahr"
        elif rp_string is None:
            return "-"
        else:
            return rp_string
    

def count_occurrence(rp_string: Optional[str], deadline: Optional[str]) -> int:
    """Berechne Anzahl der Wie"""
    if not rp_string:
        return 0
    if not deadline:
        return 0

    try:
        deadline_dt = datetime.fromisoformat(deadline)
        now = datetime.now()
        diff = deadline_dt - now
        
        valid_repeat = ["d", "w", "m", "y"]
        if diff.total_seconds() < 0 and rp_string in valid_repeat:
            return 1
        else:
            return 0
    except:
        return 0


def update_datetime(dt_string: Optional[str], original_dt: Optional[str], repeat: Optional[str], every: Optional[int], occurrence: Optional[int]) -> str:
    """Aktualisiere Datetime-String für Anzeige"""
    if not dt_string:
        return "-"
    if not original_dt:
        return "Fehler: importieren der Parameter-Daten"
    if not repeat:
        return dt_string
    if repeat is None:
        return dt_string
    if every is None:
        return dt_string
    if occurrence is None:
        return dt_string
    
    try:
        dt = datetime.fromisoformat(dt_string)
        o_dt = datetime.fromisoformat(original_dt)
        now = datetime.now()
        diff = dt - now

        if diff.total_seconds() < 0:
            # Tägliche Wiederholung
            if repeat == "d":
                dt = o_dt + relativedelta(days=+(occurrence*every))
            # Wöchentliche Wiederholung
            elif repeat == "w":
                dt = o_dt + relativedelta(weeks=+(occurrence*every))
            # Monatliche Wiederholung
            elif repeat == "m":
                dt = o_dt + relativedelta(months=+(occurrence*every))
            # Jährliche Wiederholung
            elif repeat == "y":
                dt = o_dt + relativedelta(years=+(occurrence*every))
            # Keine Wiederholung
            else:
                return dt_string
            
            return dt.isoformat()
        
        else:
            return dt_string
    except:
        return dt_string


def format_datetime(dt_string: Optional[str]) -> str:
    """Formatiere Datetime-String für Anzeige"""
    if not dt_string:
        return "-"
    try:
        dt = datetime.fromisoformat(dt_string)
        return dt.strftime("%A – %d.%m.%Y – %H:%M")
    except:
        return dt_string
    

def calculate_duration(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    """Berechne Dauer in Stunden"""
    if start and end:
        diff = end - start
        return round(diff.total_seconds() / 3600, 2)
    return None


def get_datetime_color(dt_string: Optional[str], status: str) -> str:
    """Bestimme Farbe basierend auf Datetime
    
    Returns:
        - red: Datetime überschritten
        - yellow: Weniger als 24h
        - white: Normal
    """
    if not dt_string:
        return "white"
    
    if status == "finished":
        return "dim"

    try:
        datetime_dt = datetime.fromisoformat(dt_string)
        now = datetime.now()
        diff = datetime_dt - now
        
        if diff.total_seconds() < 0:
            return "red"  # Überschritten
        elif diff.total_seconds() < 86400:  # 86400 Sekunden = 24 Stunden
            return "yellow"  # Weniger als 24h
        else:
            return "green"
    except:
        return "white"
    

def check_and_reactivate_todo(todo: dict):
    """Reaktiviere ToDo deren Deadline bereits abgelaufen ist"""

    now = datetime.now()
    reactivated = False

    if todo["status"] == "completed":
        deadline = todo.get("deadline")

        if deadline and datetime.fromisoformat(deadline) < now:
            todo["status"] = "working"
            reactivated = True

        save_todo(todo)
    
    return reactivated


@app.command()
def create(
    title: str = typer.Argument(..., help="Titel der ToDo"),
    description: str = typer.Option("", "--description", help="Beschreibung der ToDo"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priorität: low/medium/high/urgent"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="Start-Time im Format: DD.MM.YYYY-HH:MM"),
    deadline: Optional[str] = typer.Option(None, "--deadline", "-d", help="Deadline im Format: DD.MM.YYYY-HH:MM"),
    repeat: Optional[str] = typer.Option(None, "--repeat", "-r", help="Wiederholung: 'd' = täglich, 'w' = wöchentlich, 'm' = monatlich, 'y' = jährlich"),
    every: int = typer.Option(1, "--every", "-e", help="Anpassungen der Wiederholungen (z.B. -e 4 = alle 4 d/w/m/y)")
):
    """Erstelle eine neue ToDo"""
    ensure_directories()
    
    # Validiere Priorität
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        console.print(f"[red]Fehler:[/red] Priorität muss einer sein von: {', '.join(valid_priorities)}")
        raise typer.Exit(1)
    
    # Validiere und konvertiere Start-Time
    start_iso = None
    start_dt = None
    if start:
        try:
            # Bevorzugtes Format: dd.mm.yyyy - HH:MM
            start_clean = start.replace(".", "-").replace(":", "-").replace(" ", "-")
            parts = [p for p in start_clean.split("-") if p]

            if len(parts) != 5:
                raise ValueError("Bitte Datum und Zeit angeben (z.B. 15.02.2026 14:30)")

            ## Identifiziere das Jahr
            if len(parts[0]) == 4:      # Format: yyyy-mm-dd-HH-MM
                year, month, day = parts[0], parts[1], parts[2]
            elif len(parts[2]) == 4:    # Format: dd-mm-yyyy-HH-MM 
                day, month, year = parts[0], parts[1], parts[2]
            else:
                raise ValueError("Keine gültige Jahreszahl gefunden.")

            start_str = f"{day}-{month}-{year} {parts[3]}:{parts[4]}"
            start_dt = datetime.strptime(start_str, "%d-%m-%Y %H:%M")
            start_iso = start_dt.isoformat()

        except:
            console.print("[red]Fehler:[/red] Start-Format ungültig. Nutze: dd.mm.yyyy-HH:MM")
            console.print("[yellow]Beispiel:[/yellow] 15.02.2026-14:30")
            raise typer.Exit(1)
    
    # Validiere und konvertiere Deadline
    deadline_iso = None
    deadline_dt = None
    if deadline:
        try:
            # Bevorzugtes Format: dd.mm.yyyy - HH:MM
            deadline_clean = deadline.replace(".", "-").replace(":", "-").replace(" ", "-")
            parts = [p for p in deadline_clean.split("-") if p]

            if len(parts) != 5:
                raise ValueError("Bitte Datum und Zeit angeben (z.B. 15.02.2026 14:30)")

            ## Identifiziere das Jahr
            if len(parts[0]) == 4:      # Format: yyyy-mm-dd-HH-MM
                year, month, day = parts[0], parts[1], parts[2]
            elif len(parts[2]) == 4:    # Format: dd-mm-yyyy-HH-MM 
                day, month, year = parts[0], parts[1], parts[2]
            else:
                raise ValueError("Keine gültige Jahreszahl gefunden.")

            deadline_str = f"{day}-{month}-{year} {parts[3]}:{parts[4]}"
            deadline_dt = datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
            deadline_iso = deadline_dt.isoformat()

        except:
            console.print("[red]Fehler:[/red] Deadline-Format ungültig. Nutze: dd.mm.yyyy-HH:MM")
            console.print("[yellow]Beispiel:[/yellow] 15.02.2026-14:30")
            raise typer.Exit(1)
        
    # Validiere Wiederholungen
    valid_repeat = [None, "d", "w", "m", "y"]
    if repeat not in valid_repeat:
        console.print(f"[red]Fehler:[/red] Wiederholung muss einer sein von: {', '.join(valid_repeat)}")
        raise typer.Exit(1)
    
    # Erstelle ToDo-Daten
    todo_data = {
        "id": get_next_id(),
        "title": title,
        "description": description,
        "priority": priority,
        "status": "working",
        "start_time": start_iso,
        "original_start_time": start_iso,
        "deadline": deadline_iso,
        "original_deadline": deadline_iso,
        "duration_hours": calculate_duration(start_dt, deadline_dt),
        "repeat": repeat,
        "repeat_every": every,
        "occurrence_count": 0,
        "completion_history": [],
        "created_at": datetime.now().isoformat(),
        "finished_at": None
    }
    
    # Speichere ToDo
    save_todo(todo_data, "working")
    
    console.print(f"[green]✓[/green] ToDo erstellt mit ID: [bold]{todo_data['id']}[/bold]")


@app.command()
def list(
    all: bool = typer.Option(False, "--all", "-a", help="Zeige auch abgeschlossene ToDos"),
    finished: bool = typer.Option(False, "--finished", "-f", help="Zeige nur abgeschlossene ToDos"),
):
    """Liste alle ToDos auf"""
    ensure_directories()
    todo_dir = get_todo_dir()

    # Sammle ToDos
    todos = []

    if not finished:
        # Working ToDos
        for todo_file in sorted((todo_dir / "working").glob("*.json")):
            with open(todo_file, "r") as f:
                todos.append(json.load(f))

    if all or finished:
        # Finished ToDos
        for todo_file in sorted((todo_dir / "finished").glob("*.json")):
            with open(todo_file, "r") as f:
                todos.append(json.load(f))

    if not todos:
        console.print("[yellow]Keine ToDos gefunden.[/yellow]")
        return

    # Erstelle Tabelle
    table = Table(title="📝 Deine ToDos")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Titel", style="white")
    table.add_column("Priorität", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Start", style="yellow")
    table.add_column("Deadline", style="yellow")
    table.add_column("Wiederholung", style="blue")

    reactivated_count = 0
    new_todos = []

    for todo in sorted(todos, key=lambda x: x["deadline"]):
        # Reaktiviere ToDo
        reactivated = check_and_reactivate_todo(todo)
        if reactivated == True:
            reactivated_count += 1

        # Ausblenden der erledigten
        if todo["status"] == "completed":
            continue

        # Anpassungen
        if todo["repeat"]:
            todo["occurrence_count"] += count_occurrence(todo["repeat"], todo["deadline"])

        if todo["start_time"]:
            todo["start_time"] = update_datetime(todo["start_time"], todo["original_start_time"], todo["repeat"], todo["repeat_every"], todo["occurrence_count"])
        
        if todo["deadline"]:
            todo["deadline"] = update_datetime(todo["deadline"], todo["original_deadline"], todo["repeat"], todo["repeat_every"], todo["occurrence_count"])

        new_todos.append(todo)


    for todo in sorted(new_todos, key=lambda x: x["deadline"]):
        # # Reaktiviere ToDo
        # reactivated = check_and_reactivate_todo(todo)
        # if reactivated == True:
        #     reactivated_count += 1

        # # Ausblenden der erledigten
        # if todo["status"] == "completed":
        #     continue

        # Farbe für Status
        status_color = "green" if todo["status"] == "working" else "dim"

        # #Wiederholung-Anpassungen
        repeat_formatted = format_repeat(todo["repeat"], todo["repeat_every"])
        # todo["occurrence_count"] += count_occurrence(todo["repeat"], todo["deadline"])

        # Start(-Time)-Anpassungen
        # todo["start_time"] = update_datetime(todo["start_time"], todo["original_start_time"], todo["repeat"], todo["repeat_every"], todo["occurrence_count"])
        start_time_color = get_datetime_color(todo["start_time"], todo["status"])
        start_time_formatted = format_datetime(todo["start_time"])

        # Deadline-Anpassungen
        # todo["deadline"] = update_datetime(todo["deadline"], todo["original_deadline"], todo["repeat"], todo["repeat_every"], todo["occurrence_count"])
        deadline_color = get_datetime_color(todo["deadline"], todo["status"])
        deadline_formatted = format_datetime(todo["deadline"])

        table.add_row(
            str(todo["id"]),
            todo["title"],
            todo["priority"],
            f"[{status_color}]{todo["status"]}[/{status_color}]",
            f"[{start_time_color}]{start_time_formatted}[/{start_time_color}]",
            f"[{deadline_color}]{deadline_formatted}[/{deadline_color}]",
            f"{repeat_formatted}"
        )

    console.print(table)
    if reactivated_count > 0:
        console.print(f"[dim]{reactivated_count} ToDos reaktiviert![/dim]")


@app.command()
def show(todo_id: int = typer.Argument(..., help="ID der ToDo")):
    """Zeige Details einer ToDo"""
    todo_data, _ = load_todo(todo_id)

    if not todo_data:
        console.print(f"[red]Fehler:[/red] ToDo mit ID {todo_id} nicht gefunden.")
        raise typer.Exit(1)
    
    # Überprüfe Reaktivierung
    reactivated = check_and_reactivate_todo(todo_data)
    if reactivated == True:
        console.print("[dim]ToDo wurde reaktiviert![/dim]")
    
    #Wiederholung-Anpassungen
    repeat_formatted = format_repeat(todo_data["repeat"], todo_data["repeat_every"])
    todo_data["occurrence_count"] += count_occurrence(todo_data["repeat"], todo_data["deadline"])

    # Duration-Anpassung
    duration = False
    if todo_data["start_time"] is None or todo_data["deadline"] is None:
        duration = False
    else: 
        duration = True

    # Start(-Time)-Anpassungen
    todo_data["start_time"] = update_datetime(todo_data["start_time"], todo_data["original_start_time"], todo_data["repeat"], todo_data["repeat_every"], todo_data["occurrence_count"])
    start_time_color = get_datetime_color(todo_data["start_time"], todo_data["status"])
    start_time_formatted = format_datetime(todo_data["start_time"])

    # Deadline-Anpassungen
    todo_data["deadline"] = update_datetime(todo_data["deadline"], todo_data["original_deadline"], todo_data["repeat"], todo_data["repeat_every"], todo_data["occurrence_count"])
    deadline_color = get_datetime_color(todo_data["deadline"], todo_data["status"])
    deadline_formatted = format_datetime(todo_data["deadline"])
    
    # Erstelle Detail-Ansicht
    console.print(f"\n[bold cyan]ToDo #{todo_data["id"]}[/bold cyan]")
    console.print("[bold]Titel:[/bold]")
    console.print(f"    {todo_data["title"]}")
    console.print("[bold]Beschreibung:[/bold]")
    console.print(f"    {todo_data["description"] or "---"}")
    console.print("[bold]Priorität:[/bold]")
    console.print(f"    {todo_data["priority"]}")
    console.print("[bold]Status:[/bold]")
    console.print(f"    {todo_data["status"]}")
    console.print("[bold]Start:[/bold]")
    console.print(f"    [{start_time_color}]{start_time_formatted}[/{start_time_color}]")
    console.print("[bold]Deadline:[/bold]")
    console.print(f"    [{deadline_color}]{deadline_formatted}[/{deadline_color}]")

    if duration:
        console.print("[bold]Dauer:[/bold]")
        console.print(f"    {todo_data["duration_hours"]} Stunden")

    if todo_data["repeat"] is not None:
        console.print("[bold]Wiederholung:[/bold]")
        console.print(f"    {repeat_formatted}")

    console.print("[bold]Erstellt am:[/bold]")
    console.print(f"    {format_datetime(todo_data["created_at"])}")

    if todo_data["completion_history"]:
        console.print("[bold]Completion-History:[/bold]")
        for comp in todo_data["completion_history"]:
            console.print(f"    {format_datetime(comp)}")

    if todo_data["finished_at"]:
        console.print("[bold]Abgeschlossen am:[/bold]")
        console.print(f"    {format_datetime(todo_data["finished_at"])}")

    console.print()


@app.command()
def update(
    todo_id: int = typer.Argument(..., help="ID der ToDo"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Neuer Titel"),
    description: Optional[str] = typer.Option(None, "--description", help="Neue Beschreibung"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Neue Priorität"),
    start_time: Optional[str] = typer.Option(None, "--start-time", "-s", help="Start im Format: DD.MM.YYYY-HH:MM"),
    deadline: Optional[str] = typer.Option(None, "--deadline", "-d", help="Deadline im Format: DD.MM.YYYY-HH:MM"),
    repeat: Optional[str] = typer.Option(None, "--repeat", "-r", help="Wiederholung: 'd' = täglich, 'w' = wöchentlich, 'm' = monatlich, 'y' = jährlich"),
    every: int = typer.Option(None, "--every", "-e", help="Anpassungen der Wiederholungen (z.B. -e 4 = alle 4 d/w/m/y)"),
    completed: bool = typer.Option(False, "--completed", "-c", help="Beenden der ToDo nur für die aktuelle Deadline"),
    finished: bool = typer.Option(False, "--finished", "-f", help="Als abgeschlossen markieren")
):
    """Aktualisiere eine ToDo"""
    todo_data, old_path = load_todo(todo_id)

    if not todo_data:
        console.print(f"[red]Fehler:[/red] ToDo mit ID {todo_id} nicht gefunden.")
        raise typer.Exit(1)
    
    # Aktualisiere Felder
    if title:
        todo_data["title"] = title

    if description is not None:
        todo_data["description"] = description

    if priority:
        valid_priorities = ["low", "medium", "high", "urgent"]
        if priority not in valid_priorities:
            console.print(f"[red]Fehler:[/red] Priorität muss einer sein von: {", ".join(valid_priorities)}")
            raise typer.Exit(1)
        todo_data["priority"] = priority

    if deadline:
        deadline_iso = None
        try:
            # Bevorzugtes Format: dd.mm.yyyy - HH:MM
            deadline_clean = deadline.replace(".", "-").replace(":", "-").replace(" ", "-")
            parts = [p for p in deadline_clean.split("-") if p]

            if len(parts) != 5:
                raise ValueError("Bitte Datum und Zeit angeben (z.B. 15.02.2026-14:30)")

            ## Identifiziere das Jahr
            if len(parts[0]) == 4:      # Format: yyyy-mm-dd-HH-MM
                year, month, day = parts[0], parts[1], parts[2]
            elif len(parts[2]) == 4:    # Format: dd-mm-yyyy-HH-MM 
                day, month, year = parts[0], parts[1], parts[2]
            else:
                raise ValueError("Keine gültige Jahreszahl gefunden (richtiges Beispiel: 15.02.2026-14:30 oder 2026.02.15-14:30)")

            deadline_str = f"{day}-{month}-{year} {parts[3]}:{parts[4]}"
            deadline_dt = datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
            deadline_iso = deadline_dt.isoformat()
        except:
            console.print("[red]Fehler:[/red] Deadline-Format ungültig. Nutze: dd.mm.yyyy-HH:MM")
            console.print("[yellow]Beispiel:[/yellow] 15.02.2026-14:30")
            raise typer.Exit(1)
        
        todo_data["deadline"] = deadline_iso
        todo_data["original_deadline"] = deadline_iso

    if start_time:
        start_iso = None
        try:
            # Bevorzugtes Format dd.mm.yyyy-HH:MM
            start_clean = start_time.replace(".", "-").replace(":", "-").replace(" ", "-")
            parts = [p for p in start_clean.split("-") if p]

            if len(parts) != 5:
                raise ValueError("Bitte Datum und Zeit angeben (z.B. 15.02.2026-08:30)")
            
            # Identifiziere das Jahr
            if len(parts[0]) == 4:      # Format: yyyy-mm-dd-HH-MM
                year, month, day = parts[0], parts[1], parts[2]
            elif len(parts[2]) == 4:    # Format: dd-mm-yyyy-HH-MM
                day, month, year = parts[0], parts[1], parts[2]
            else:
                raise ValueError("Keine gültige Jahreszahl gefunden (richtiges Beispiel: 15.02.2026-08:30 oder 2026.02.15-08:30)")
            
            start_str = f"{day}-{month}-{year} {parts[3]}:{parts[4]}"
            start_dt = datetime.strptime(start_str, "%d-%m-%Y %H:%M")
            start_iso = start_dt.isoformat()
        except:
            console.print("[red]Fehler:[/red] Start-Time-Format ungültig. Nutze: dd.mm.yyyy-HH:MM")
            console.print("[yellow]Beispiel:[/yellow] 15.02.2026-08:30")
            raise typer.Exit
        
        todo_data["start_time"] = start_iso
        todo_data["original_start_time"] = start_iso
        
    if repeat:
        valid_repeat = [None, "d", "w", "m", "y"]
        if repeat not in valid_repeat:
            console.print(f"[red]Fehler:[/red] Wiederholung muss einer sein von: {', '.join(valid_repeat)}")
            raise typer.Exit(1)
        todo_data["repeat"] = repeat

    if every:
        todo_data["every"] = every

    # Status auf completed setzen
    if completed and todo_data["status"] != "finished":
        todo_data["status"] = "completed"

        now = datetime.now().isoformat()
        todo_data["completion_history"].append(now)

        console.print(f"[green]✓[/green] ToDo #{todo_id} als erledigt markiert!")
        console.print(f"[dim]Erledigt am: {format_datetime(now)}[/dim]")

    # Status auf finished setzen
    if finished and todo_data["status"] == "working" and old_path is not None:
        todo_data["status"] = "finished"
        todo_data["finished_at"] = datetime.now().isoformat()

        # Alte Datei löschen
        old_path.unlink()

        # In finished/ speichern
        save_todo(todo_data, "finished")

        console.print(f"[green]✓[/green] ToDo #{todo_id} als abgeschlossen markiert und verschoben!")
    else:
        # Normale Aktualisierung
        save_todo(todo_data, todo_data["status"])
        console.print(f"[green]✓[/green] ToDo #{todo_id} aktualisiert!")


@app.command()
def delete(
    todo_id: int = typer.Argument(..., help="ID der ToDo"),
    force: bool = typer.Option(False, "--force", "-f", help="Ohne Bestätigung löschen")
):
    """Lösche eine ToDo"""
    todo_data, todo_path = load_todo(todo_id)

    if not todo_data:
        console.print(f"[red]Fehler:[/red] ToDo mit ID {todo_id} nicht gefunden.")
        raise typer.Exit(1)
    
    # Bestätigung (ohne --force)
    if not force:
        confirm = typer.confirm(f"ToDo '{todo_data["title"]}' wirklich löschen?")
        if not confirm: 
            console.print("[yellow]Abgebrochen.[/yellow]")
            raise typer.Exit()

    if todo_path == None:
        console.print(f"[red]Fehler:[/red] Pfad der ToDo mit ID {todo_id} nicht gefunden.")
        raise typer.Exit(1)

    # Lösche Datei
    todo_path.unlink()
    console.print(f"[green]✓[/green] ToDo #{todo_id} gelöscht!")


@app.command()
def migrate():
    """Migriere alle ToDos auf aktuelles Schema"""

    todo_dir = get_todo_dir()
    migrated_count = 0
    error_count = 0
    added_fields = set()    # Tracking welche Felder hinzugefügt wurden

    # Beide Ordner durchgehen
    for folder in ["working", "finished"]:
        folder_path = todo_dir / folder

        if not folder_path.exists():
            continue

        for file in folder_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    todo = json.load(f)

                # Abspeichern der fehlenden Felder vor der Migration
                schema = get_todo_schema()
                missing_fields = [field for field in schema.keys() if field not in todo]

                if missing_fields:
                    # Migration
                    todo = migrate_todo_data(todo)

                    # Speichere
                    with open(file, "w") as f:
                        json.dump(todo, f, indent=2, ensure_ascii=False)

                    migrated_count += 1
                    added_fields.update(missing_fields)
                    console.print(f"[green]✓[/green] {todo.get("title", "Unbekannt")} (ID: {todo.get("id")}) - {len(missing_fields)} Felder hinzugefügt")

            except Exception as e:
                error_count += 1
                console.print(f"[red]x[/red] Fehler bei {file.name}: {e}")

    if migrated_count > 0:
        console.print(f"[green bold]✓ Migration abgeschlossen![/green bold]")
        console.print(f"  Migriert: {migrated_count} ToDos")
        console.print(f"  Hinzugefügte Felder: {", ".join(sorted(added_fields))}")
    else:
        console.print("[yellow]Alle ToDos sind bereits aktuell.[/yellow]")

    if error_count > 0:
        console.print(f"[red]Fehler: {error_count} ToDos[/red]")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Zeige aktuelle Konfiguration"),
    set_dir: Optional[str] = typer.Option(None, "--set-dir", help="Setze ToDo-Verzeichnis")
):
    """Verwalte die Konfiguration"""
    if show: 
        config = get_config()
        console.print("[bold]Aktuelle Konfiguration:[/bold]")
        console.print(f"ToDo-Verzeichnis: [cyan]{config["todo_dir"]}[/cyan]")
        return
    
    if set_dir:
        new_dir = Path(set_dir).expanduser().resolve()
        config = get_config()
        config["todo_dir"] = str(new_dir)
        save_config(config)
        ensure_directories()
        console.print(f"[green]✓[/green] ToDo-Verzeichnis gesetzt aus: [cyan]{new_dir}[/cyan]")
        return
    
    # Wenn keine Option angegeben, zeige Hilfe
    console.print("[yellow] Nutze --show oder --set-dir[/yellow]")
    console.print("Beispiel: [cyan]todo config --show[/cyan]")


if __name__ == "__main__":
    app()
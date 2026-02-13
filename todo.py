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
            return json.load(f), working_file
    
    # Suche in finished/
    finished_file = todo_dir / "finished" / f"{todo_id}.json"
    if finished_file.exists():
        with open(finished_file, "r") as f:
            return json.load(f), finished_file
    
    return None, None


def save_todo(todo_data: dict, status: str = "working"):
    """Speichere eine ToDo"""
    ensure_directories()
    todo_dir = get_todo_dir()
    filename = f"{todo_data['id']}.json"
    filepath = todo_dir / status / filename
    
    with open(filepath, "w") as f:
        json.dump(todo_data, f, indent=4)
    

def format_repeat(rp_string: Optional[str]) -> str:
    """Formatiere Repeat-String für Anzeige"""
    if not rp_string:
        return "-"
    
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


def update_deadline(dt_string: Optional[str], original_dt: Optional[str], repeat: Optional[str], occurrence: Optional[int]) -> str:
    """Aktualisiere Datetime-String für Anzeige"""
    if not dt_string:
        return "-"
    if not original_dt:
        return "-"
    if not repeat:
        return "-"
    if repeat is None:
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
                dt = o_dt + relativedelta(days=+occurrence)
            # Wöchentliche Wiederholung
            elif repeat == "w":
                dt = o_dt + relativedelta(weeks=+occurrence)
            # Monatliche Wiederholung
            elif repeat == "m":
                dt = o_dt + relativedelta(months=+occurrence)
            # Jährliche Wiederholung
            elif repeat == "y":
                dt = o_dt + relativedelta(years=+occurrence)
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


def get_deadline_color(deadline: Optional[str]) -> str:
    """Bestimme Farbe basierend auf Deadline
    
    Returns:
        - red: Deadline überschritten
        - yellow: Weniger als 24h
        - white: Normal
    """
    if not deadline:
        return "white"

    try:
        deadline_dt = datetime.fromisoformat(deadline)
        now = datetime.now()
        diff = deadline_dt - now
        
        if diff.total_seconds() < 0:
            return "red"  # Überschritten
        elif diff.total_seconds() < 86400:  # 86400 Sekunden = 24 Stunden
            return "yellow"  # Weniger als 24h
        else:
            return "green"
    except:
        return "white"
    

@app.command()
def create(
    title: str = typer.Argument(..., help="Titel der ToDo"),
    description: str = typer.Option("", "--description", "-d", help="Beschreibung der ToDo"),
    priority: str = typer.Option("medium", "--priority", "-p", help="Priorität: low/medium/high/urgent"),
    deadline: Optional[str] = typer.Option(None, "--deadline", help="Deadline im Format: YYYY.MM.DD-HH:MM"),
    repeat: Optional[str] = typer.Option(None, "--repeat", "-r", help="Wiederholung: 'd' = täglich, 'w' = wöchentlich, 'm' = monatlich, 'y' = jährlich")
):
    """Erstelle eine neue ToDo"""
    ensure_directories()
    
    # Validiere Priorität
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        console.print(f"[red]Fehler:[/red] Priorität muss einer sein von: {', '.join(valid_priorities)}")
        raise typer.Exit(1)
    
    # Validiere und konvertiere Deadline
    deadline_iso = None
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
        "deadline": deadline_iso,
        "original_deadline": deadline_iso,
        "repeat": repeat,
        "occurrence_count": 0,
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
    table.add_column("Deadline", style="yellow")
    table.add_column("Wiederholung", style="blue")

    for todo in sorted(todos, key=lambda x: x["id"]):
        # Farbe für Status
        status_color = "green" if todo["status"] == "working" else "dim"

        #Wiederholung-Anpassungen
        repeat_formatted = format_repeat(todo["repeat"])
        todo["occurrence_count"] += count_occurrence(todo["repeat"], todo["deadline"])

        # Deadline-Anpassungen
        todo["deadline"] = update_deadline(todo["deadline"], todo["original_deadline"], todo["repeat"], todo["occurrence_count"])
        deadline_color = get_deadline_color(todo["deadline"])
        deadline_formatted = format_datetime(todo["deadline"])

        table.add_row(
            str(todo["id"]),
            todo["title"],
            todo["priority"],
            f"[{status_color}]{todo["status"]}[/{status_color}]",
            f"[{deadline_color}]{deadline_formatted}[/{deadline_color}]",
            f"{repeat_formatted}"
        )

    console.print(table)



@app.command()
def show(todo_id: int = typer.Argument(..., help="ID der ToDo")):
    """Zeige Details einer ToDo"""
    todo_data, _ = load_todo(todo_id)

    if not todo_data:
        console.print(f"[red]Fehler:[/red] ToDo mit ID {todo_id} nicht gefunden.")
        raise typer.Exit(1)
    
    #Wiederholung-Anpassungen
    repeat_formatted = format_repeat(todo_data["repeat"])
    todo_data["occurrence_count"] += count_occurrence(todo_data["repeat"], todo_data["deadline"])

    # Deadline-Anpassungen
    todo_data["deadline"] = update_deadline(todo_data["deadline"], todo_data["original_deadline"], todo_data["repeat"], todo_data["occurrence_count"])
    deadline_color = get_deadline_color(todo_data["deadline"])
    deadline_formatted = format_datetime(todo_data["deadline"])
    
    # Erstelle Detail-Ansicht
    console.print(f"\n[bold cyan]ToDo #{todo_data["id"]}[/bold cyan]")
    console.print(f"[bold]Titel:[/bold] {todo_data["title"]}")
    console.print(f"[bold]Beschreibung:[/bold] {todo_data["description"] or "---"}")
    console.print(f"[bold]Priorität:[/bold] {todo_data["priority"]}")
    console.print(f"[bold]Status:[/bold] {todo_data["status"]}")
    console.print(f"[bold]Deadline:[/bold] [{deadline_color}]{deadline_formatted}[/{deadline_color}]")
    console.print(f"[bold]Wiederholung:[/bold] {repeat_formatted}")
    console.print(f"[bold]Erstellt am:[/bold] {format_datetime(todo_data["created_at"])}")

    if todo_data["finished_at"]:
        console.print(f"[bold]Abgeschlossen am:[/bold] {format_datetime(todo_data["finished_at"])}")

    console.print()



@app.command()
def update(
    todo_id: int = typer.Argument(..., help="ID der ToDo"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Neuer Titel"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Neue Beschreibung"),
    priority: Optional[str] = typer.Option(None, "--priority", "-p", help="Neue Priorität"),
    deadline: Optional[str] = typer.Option(None, "--deadline", help="Deadline im Format: YYYY.MM.DD-HH:MM"),
    repeat: Optional[str] = typer.Option(None, "--repeat", "-r", help="Wiederholung: 'd' = täglich, 'w' = wöchentlich, 'm' = monatlich, 'y' = jährlich"),
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
        
        todo_data["deadline"] = deadline_iso
    if repeat:
        valid_repeat = [None, "d", "w", "m", "y"]
        if repeat not in valid_repeat:
            console.print(f"[red]Fehler:[/red] Wiederholung muss einer sein von: {', '.join(valid_repeat)}")
            raise typer.Exit(1)
        todo_data["repeat"] = repeat

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
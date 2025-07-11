from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from rich.align import Align
import sqlite3
import subprocess
import os

console = Console()

def connect_db():
    return sqlite3.connect("syncnet.db")


def show_dashboard(user):
    console.clear()
    role = user["role"]
    user_id = user["user_id"]
    name = user["name"]

    console.rule(f"[bold magenta]📊 {role} Dashboard", style="bright_magenta")
    console.print(Panel.fit(
        f"[bold white]Welcome, {name}![/bold white]\nUser ID: [green]{user_id}[/green]\nRole: [cyan]{role}[/cyan]",
        title="👋 Logged In",
        box=box.ROUNDED,
        border_style="green"
    ))

    while True:
        console.print("\n[bold cyan]✨ Choose an action:[/bold cyan]")

        # Dynamic menu based on role
        if role == "Suppliers":
            console.print("[bold green]1.[/bold green] 🏢 View listed Warehouses")
        elif role == "Warehouses":
            console.print("[bold green]1.[/bold green] 🏭 View listed Suppliers")
            console.print("[bold green]2.[/bold green] 🏬 View listed Regional Hubs")
        elif role == "RegionalHubs":
            console.print("[bold green]1.[/bold green] 🏢 View listed Warehouses")

        console.print("[bold blue]3.[/bold blue] 🤝 Start a Group (Network Scan)")
        console.print("[bold yellow]9.[/bold yellow] 🧾 View my registration details")
        console.print("[bold red]0.[/bold red] 🔒 Logout")

        valid_choices = {
            "Suppliers": ["1", "3", "9", "0"],
            "Warehouses": ["1", "2", "3", "9", "0"],
            "RegionalHubs": ["1", "3", "9", "0"]
        }

        choice = Prompt.ask("\n[bold white]Enter your choice[/bold white]", choices=valid_choices[role])

        if choice == "1":
            if role == "Suppliers":
                show_listed_warehouses()
            elif role == "Warehouses":
                show_listed_suppliers()
            elif role == "RegionalHubs":
                show_listed_warehouses()

        elif choice == "2" and role == "Warehouses":
            show_listed_hubs()

        elif choice == "3":
            start_group()

        elif choice == "9":
            show_user_details(role, user_id)

        elif choice == "0":
            console.print("\n[bold red]👋 Logging out... Returning to main menu.[/bold red]")
            break


def start_group():
    console.print("\n[bold cyan]🚀 Starting group scan using Network Scanner...[/bold cyan]")

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "network_scan.py"))

    if not os.path.exists(script_path):
        console.print(f"[red]❌ Cannot find network_scan.py at: {script_path}[/red]")
        return

    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to run network scan: {e}[/red]")


def show_listed_warehouses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT warehouse_id, warehouse_name, location FROM Warehouses")
    data = cursor.fetchall()
    conn.close()
    show_table("🏢 Available Warehouses", ["ID", "Name", "Location"], data)


def show_listed_suppliers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT supplier_id, supplier_name, contact_number FROM Suppliers")
    data = cursor.fetchall()
    conn.close()
    show_table("🏭 Listed Suppliers", ["ID", "Name", "Contact"], data)


def show_listed_hubs():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT hub_id, hub_name, location FROM RegionalHubs")
    data = cursor.fetchall()
    conn.close()
    show_table("🏬 Listed Regional Hubs", ["ID", "Name", "Location"], data)


def show_user_details(role, user_id):
    conn = connect_db()
    cursor = conn.cursor()

    if role == "Suppliers":
        cursor.execute("""
            SELECT supplier_name, contact_number, user_id, ip_address, date_of_joining
            FROM Suppliers WHERE user_id = ?""", (user_id,))
        data = cursor.fetchone()
        labels = ["Name", "Contact", "User ID", "IP Address", "Joining Date"]

    elif role == "Warehouses":
        cursor.execute("""
            SELECT warehouse_name, location, contact_number, user_id, ip_address, hub_id, date_of_joining
            FROM Warehouses WHERE user_id = ?""", (user_id,))
        data = cursor.fetchone()
        labels = ["Name", "Location", "Contact", "User ID", "IP Address", "Hub ID", "Joining Date"]

    elif role == "RegionalHubs":
        cursor.execute("""
            SELECT hub_name, location, contact_number, user_id, ip_address, date_of_establishment
            FROM RegionalHubs WHERE user_id = ?""", (user_id,))
        data = cursor.fetchone()
        labels = ["Name", "Location", "Contact", "User ID", "IP Address", "Establishment Date"]

    conn.close()

    if data:
        info = "\n".join([f"[bold]{label}:[/bold] {value}" for label, value in zip(labels, data)])
        panel_width = min(console.width - 10, 80)
        console.print(Panel(info, title="🧾 Your Registration Details", box=box.DOUBLE, border_style="bright_yellow", width=panel_width))
    else:
        console.print("[red]❌ Could not fetch user details.[/red]")


def show_table(title, columns, rows):
    if not rows:
        console.print(f"[yellow]⚠️ No data available for: {title}[/yellow]")
        return

    table = Table(
        title=title,
        title_style="bold bright_blue",
        box=box.HEAVY_EDGE,
        header_style="bold cyan",
        border_style="blue",
        show_lines=True,
        padding=(0, 1),
    )

    for col in columns:
        table.add_column(col, style="white", justify="center")

    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    centered_table = Align.center(table, vertical="middle")
    console.print(centered_table)

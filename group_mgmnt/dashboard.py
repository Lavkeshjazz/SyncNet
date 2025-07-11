from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
from rich.align import Align
import sqlite3
import subprocess
import sys
import os

sys.path.append(os.path.abspath(".."))

from secr import SecureSender
from discovery_ui import ReceiverServiceBrowser

console = Console()

def connect_db():
    return sqlite3.connect("syncnet.db")

def show_dashboard(user):
    console.clear()
    user_id = user["user_id"]
    name = user["name"]

    console.rule(f"[bold magenta]📊 User Dashboard", style="bright_magenta")
    console.print(Panel.fit(
        f"[bold white]Welcome, {name}![/bold white]\nUser ID: [green]{user_id}[/green]",
        title="👋 Logged In",
        box=box.ROUNDED,
        border_style="green"
    ))

    while True:
        console.print("\n[bold cyan]✨ Choose an action:[/bold cyan]")
        console.print("[bold green]1.[/bold green] 🏢 View listed Warehouses")
        console.print("[bold green]2.[/bold green] 🏭 View listed Suppliers")
        console.print("[bold green]3.[/bold green] 🏬 View listed Regional Hubs")
        console.print("[bold blue]4.[/bold blue] 📤 Send Orders")
        console.print("[bold blue]5.[/bold blue] 📥 Receive Orders")
        console.print("[bold yellow]9.[/bold yellow] 🧾 View my registration details")
        console.print("[bold red]0.[/bold red] 🔒 Logout")

        choice = Prompt.ask("\n[bold white]Enter your choice[/bold white]", choices=["1", "2", "3", "4", "5", "9", "0"])

        if choice == "1":
            show_listed_warehouses()
        elif choice == "2":
            show_listed_suppliers()
        elif choice == "3":
            show_listed_hubs()
        elif choice == "4":
            console.print("[cyan]Launching Secure Sender...[/cyan]")
            sender = SecureSender()
            sender.run()
        elif choice == "5":
            console.print("[cyan]Launching Secure Receiver...[/cyan]")
            receiver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Secure_Receiver.py"))
            syncnet_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            subprocess.run(["python", receiver_path], cwd=syncnet_dir)
        elif choice == "9":
            show_user_details(user_id)
        elif choice == "0":
            console.print("[bold red]Logging out...[/bold red]")
            break

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

def show_user_details(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    role_tables = [
        ("Suppliers", "supplier_name", "date_of_joining"),
        ("Warehouses", "warehouse_name", "date_of_joining"),
        ("RegionalHubs", "hub_name", "date_of_establishment")
    ]

    data = None
    for table, name_col, date_col in role_tables:
        cursor.execute(f"""
            SELECT {name_col}, user_id, ip_address, {date_col}
            FROM {table}
            WHERE user_id = ?
        """, (user_id,))
        data = cursor.fetchone()
        if data:
            break

    conn.close()

    if data:
        labels = ["Name", "User ID", "IP Address", "Joining Date"]
        info = "\n".join([f"[bold]{label}:[/bold] {value}" for label, value in zip(labels, data)])
        panel_width = min(console.width - 10, 80)
        console.print(Panel(info, title="🧾 Your Registration Details", box=box.DOUBLE, border_style="bright_yellow", width=panel_width))
    else:
        console.print("[red]❌ Could not fetch user details.[/red]")


def show_table(title, columns, rows):
    if not rows:
        console.print(f"[yellow]⚠️ No data available for: {title}[/yellow]")
        return

    from rich.table import Table
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

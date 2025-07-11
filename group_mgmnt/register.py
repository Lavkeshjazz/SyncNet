# register.py

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import box
import sqlite3
import datetime
import hashlib
from socket_utils import get_ip_address

console = Console()

def connect_db():
    return sqlite3.connect("syncnet.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user():
    console.clear()
    console.rule("[bold magenta]📝 SyncNet Registration Portal")

    console.print(
        Panel.fit(
            "[bold cyan]Register a new user for the local order network.[/bold cyan]\n"
            "[dim]Suppliers, Warehouses, and Hubs are all welcome.[/dim]",
            box=box.ROUNDED, padding=(1, 2), border_style="cyan"
        )
    )

    console.print("\n[bold blue]🔰 Select your role:[/bold blue]")
    console.print("[bold green]1.[/bold green] Supplier 🏭")
    console.print("[bold yellow]2.[/bold yellow] Warehouse 🏢")
    console.print("[bold magenta]3.[/bold magenta] Regional Hub 🏬")

    while True:
        choice = Prompt.ask("\n[bold white]Enter your choice[/bold white] ([green]1-3[/green])")
        if choice == "1":
            role = "supplier"
            break
        elif choice == "2":
            role = "warehouse"
            break
        elif choice == "3":
            role = "hub"
            break
        else:
            console.print("[red]❌ Invalid choice. Please enter 1, 2, or 3.[/red]")

    console.rule(f"[bold cyan]🗂 Registering as a {role.capitalize()}")

    name = Prompt.ask("👤 Enter [bold]name[/bold]")
    contact = Prompt.ask("📞 Enter [bold]contact number[/bold]")
    user_id = Prompt.ask("🆔 Enter [bold]User ID[/bold] (must be unique)")
    password = Prompt.ask("🔐 Enter [bold]Password[/bold]", password=True)
    hashed_pw = hash_password(password)

    # 🌐 IP address selection
    console.print("\n[bold yellow]🌐 Choose IP address input method:[/bold yellow]")
    console.print("1️⃣  Auto-detect IP address from system")
    console.print("2️⃣  Manually enter your IP address")
    ip_choice = Prompt.ask("Enter your choice", choices=["1", "2"])

    if ip_choice == "1":
        ip_address = get_ip_address()
        console.print(f"[green]✅ Auto-detected IP: [bold]{ip_address}[/bold][/green]")
    else:
        ip_address = Prompt.ask("📥 Enter your [bold]IP address[/bold] manually")
        console.print(f"[cyan]ℹ️ Using manual IP: [bold]{ip_address}[/bold][/cyan]")

    today = datetime.date.today().isoformat()

    if role == "supplier":
        register_supplier(name, contact, user_id, hashed_pw, ip_address, today)

    elif role == "warehouse":
        location = Prompt.ask("📍 Enter [bold]warehouse location[/bold]")
        hub_id = Prompt.ask("🔗 Enter [bold]associated Hub ID[/bold] (0 if unknown)", default="0")
        register_warehouse(name, location, contact, user_id, hashed_pw, ip_address, hub_id, today)

    elif role == "hub":
        location = Prompt.ask("📍 Enter [bold]hub location[/bold]")
        register_hub(name, location, contact, user_id, hashed_pw, ip_address, today)

    input("\nPress Enter to return to menu...")

def register_supplier(name, contact, user_id, password, ip, date):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Suppliers (supplier_name, contact_number, user_id, password, ip_address, orders_received, date_of_joining)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, contact, user_id, password, ip, 0, date))
        conn.commit()
        console.print(Panel.fit(f"✅ [bold green]Supplier '{name}' registered successfully![/bold green] 🎉", box=box.ROUNDED, border_style="green"))
    except Exception as e:
        console.print(f"[red]❌ Registration failed: {e}[/red]")
    finally:
        conn.close()

def register_warehouse(name, location, contact, user_id, password, ip, hub_id, date):
    conn = connect_db()
    cursor = conn.cursor()
    hub_id = int(hub_id) if hub_id.isdigit() else None
    try:
        cursor.execute('''
            INSERT INTO Warehouses (warehouse_name, location, contact_number, user_id, password, ip_address, hub_id, orders_sent, date_of_joining)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, location, contact, user_id, password, ip, hub_id, 0, date))
        conn.commit()
        console.print(Panel.fit(f"✅ [bold green]Warehouse '{name}' registered successfully![/bold green] 📦", box=box.ROUNDED, border_style="yellow"))
    except Exception as e:
        console.print(f"[red]❌ Registration failed: {e}[/red]")
    finally:
        conn.close()

def register_hub(name, location, contact, user_id, password, ip, date):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO RegionalHubs (hub_name, location, contact_number, user_id, password, ip_address, date_of_establishment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, location, contact, user_id, password, ip, date))
        conn.commit()
        console.print(Panel.fit(f"✅ [bold green]Regional Hub '{name}' registered successfully![/bold green] 🏬", box=box.ROUNDED, border_style="magenta"))
    except Exception as e:
        console.print(f"[red]❌ Registration failed: {e}[/red]")
    finally:
        conn.close()

if __name__ == "__main__":
    register_user()

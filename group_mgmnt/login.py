from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box
import sqlite3
import hashlib

# Import dashboard
from dashboard import show_dashboard

console = Console()

def connect_db():
    return sqlite3.connect("syncnet.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user():
    console.clear()
    console.rule("[bold bright_cyan]🔐 SyncNet Login Portal")

    console.print(
        Panel.fit(
            "[bold cyan]Access your account on the local order network.[/bold cyan]\n"
            "[dim]Please authenticate to continue.[/dim]",
            box=box.ROUNDED, padding=(1, 2), border_style="cyan"
        )
    )

    console.print("\n[bold blue]👤 Select your role:[/bold blue]")
    console.print("[bold green]1.[/bold green] Supplier 🏭")
    console.print("[bold yellow]2.[/bold yellow] Warehouse 🏢")
    console.print("[bold magenta]3.[/bold magenta] Regional Hub 🏬")

    while True:
        role_choice = Prompt.ask("\n[bold white]Enter your choice[/bold white] ([green]1-3[/green])")
        if role_choice == "1":
            table = "Suppliers"
            name_field = "supplier_name"
            break
        elif role_choice == "2":
            table = "Warehouses"
            name_field = "warehouse_name"
            break
        elif role_choice == "3":
            table = "RegionalHubs"
            name_field = "hub_name"
            break
        else:
            console.print("[red]❌ Invalid choice. Please enter 1, 2, or 3.[/red]")

    user_id = Prompt.ask("\n🆔 Enter your [bold]User ID[/bold]")
    password = Prompt.ask("🔑 Enter your [bold]Password[/bold]", password=True)
    hashed_pw = hash_password(password)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        f"SELECT {name_field} FROM {table} WHERE user_id = ? AND password = ?",
        (user_id, hashed_pw)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        success_msg = Text.assemble(
            ("✅ Login successful! ", "bold green"),
            ("Welcome, ", "green"),
            (f"{result[0]}", "bold cyan")
        )
        console.print(Panel(success_msg, title="Access Granted", box=box.ROUNDED, border_style="green"))
        
        # Redirect to dashboard immediately
        user_data = {"role": table, "user_id": user_id, "name": result[0]}
        show_dashboard(user_data)
    else:
        console.print(Panel("[bold red]❌ Login failed! Incorrect User ID or Password.[/bold red]",
                            title="Access Denied", border_style="red", box=box.ROUNDED))
        return None

if __name__ == "__main__":
    login_user()

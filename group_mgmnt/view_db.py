import sqlite3
from rich.console import Console
from rich.table import Table

console = Console()
conn = sqlite3.connect("syncnet.db")
cursor = conn.cursor()

def display_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        console.print(f"[bold yellow]No data found in {table_name}[/bold yellow]")
        return

    # Fetch column names
    column_names = [desc[0] for desc in cursor.description]

    # Create table using rich
    table = Table(title=table_name)
    for col in column_names:
        table.add_column(col, style="cyan")

    for row in rows:
        table.add_row(*[str(item) for item in row])

    console.print(table)

tables = ["Suppliers", "Warehouses", "RegionalHubs", "Orders"]
for t in tables:
    display_table(t)

conn.close()

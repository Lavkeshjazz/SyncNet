# welcome.py

from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich import box
import os
import time

console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def welcome_screen():
    clear()

    # Stylized ASCII logo with color gradient effect
    logo_lines = [
        ("   ███████╗██╗   ██╗███╗   ██╗ ██████╗███╗   ██╗███████╗████████╗", "bold bright_magenta"),
        ("   ██╔════╝╚██╗ ██╔╝████╗  ██║██╔════╝████╗  ██║██╔════╝╚══██╔══╝", "magenta"),
        ("   ███████╗ ╚████╔╝ ██╔██╗ ██║██║     ██╔██╗ ██║█████╗     ██║   ", "bold blue"),
        ("   ╚════██║  ╚██╔╝  ██║╚██╗██║██║     ██║╚██╗██║██╔══╝     ██║   ", "blue"),
        ("   ███████║   ██║   ██║ ╚████║╚██████╗██║ ╚████║███████╗   ██║   ", "bold bright_cyan"),
        ("   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ", "bright_black"),
    ]

    ascii_logo = Text()
    for line, style in logo_lines:
        ascii_logo.append(line + "\n", style=style)

    subtitle = Text("⛓️  Local-network ordering for Suppliers • Warehouses • Regional Hubs", style="bold white on rgb(20,90,50)")
    credit = Text("💻 Developed by Aryaman Chandra, Lavkesh Jaiswal, and Ritwik Raj", style="italic dim", justify="center")

    # Centered content
    content = Align.center(
        Text("\n") + ascii_logo + Text("\n") + subtitle + Text("\n\n") + credit,
        vertical="middle"
    )

    panel = Panel(
        content,
        title="[bold bright_cyan]syncnet",
        subtitle="📡 Terminal Interface",
        box=box.HEAVY,
        padding=(1, 4),
        border_style="bold magenta"
    )

    console.print(panel)

    with console.status("[bold cyan]Booting up SyncNet...", spinner="dots"):
        time.sleep(1.5)

    console.print("\n[bold green]✅ SyncNet is ready.[/bold green] Press [bold yellow]Enter[/bold yellow] to continue...")
    input()

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
import os
import time

console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def goodbye_screen():
    clear()

    # Static ASCII goodbye logo (all red)
    goodbye_text = Text()
    goodbye_text.append("  _____                 _ _                _ \n", style="bold red")
    goodbye_text.append(" / ____|               | | |              | |\n", style="red")
    goodbye_text.append("| |  __  ___   ___   __| | |__  _   _  ___| |\n", style="bold red")
    goodbye_text.append("| | |_ |/ _ \\ / _ \\ / _` | '_ \\| | | |/ _ \\ |\n", style="red")
    goodbye_text.append("| |__| | (_) | (_) | (_| | |_) | |_| |  __/_|\n", style="bold red")
    goodbye_text.append(" \\_____|\\___/ \\___/ \\__,_|_.__/ \\__, |\\___(_)\n", style="red")
    goodbye_text.append("                                __/ |       \n", style="red")
    goodbye_text.append("                               |___/        \n", style="red")

    # Final thank-you message
    thank_you = Text("\nThank you for using SyncNet 💻", style="bold green", justify="center")
    shutting_down = Text("System shutting down...", style="dim italic", justify="center")

    panel_content = Align.center(
        goodbye_text + Text("\n") + thank_you + Text("\n") + shutting_down,
        vertical="middle"
    )

    goodbye_panel = Panel(
        panel_content,
        title="[bold red]syncnet",
        subtitle="👋 Goodbye",
        box=box.DOUBLE,
        padding=(1, 4),
        border_style="red"
    )

    console.print(goodbye_panel)
    time.sleep(2)

    # Optional fade message
    console.print("\n[bold red]💤 Powering off...[/bold red]")
    time.sleep(1.2)
    clear()

if __name__ == "__main__":
    goodbye_screen()

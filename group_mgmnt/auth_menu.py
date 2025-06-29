from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align
from rich import box
import goodbye
import os
import time

console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def show_auth_menu():
    clear()

    # Animated banner-style heading
    heading = Text("🔐 SyncNet Access Portal", style="bold bright_cyan", justify="center")
    subtitle = Text("Choose an action to proceed", style="bold white", justify="center")

    # Styled menu options with icons
    options = Text()
    options.append(" [1] ", style="bold white")
    options.append("🔓 Login\n", style="bold green")

    options.append(" [2] ", style="bold white")
    options.append("📝 Register\n", style="bold blue")

    options.append(" [3] ", style="bold white")
    options.append("🚪 Exit\n", style="bold red")

    # Panel with styling
    panel_content = Align.center(
        Text("\n") + heading + Text("\n") + subtitle + Text("\n\n") + options,
        vertical="middle"
    )

    panel = Panel(
        panel_content,
        title="[bold bright_magenta]User Authentication",
        subtitle="🌐 Secure Local Access",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
        border_style="bold bright_magenta"
    )

    console.print(panel)

    # Input prompt
    while True:
        try:
            choice = Prompt.ask(
                "\n[bold yellow]Enter your choice[/bold yellow]",
                choices=["1", "2", "3"],
            )

            if choice == "1":
                console.print("\n[bold green]🔓 Redirecting to Login...[/bold green]")
                time.sleep(1)
                return "login"

            elif choice == "2":
                console.print("\n[bold blue]📝 Redirecting to Registration...[/bold blue]")
                time.sleep(1)
                return "register"

            elif choice == "3":
                console.print("\n[bold red]👋 Exiting SyncNet.[/bold red]")
                goodbye.goodbye_screen()
                exit()

        except KeyboardInterrupt:
            console.print("\n[bold red]❌ Interrupted. Exiting...[/bold red]")
            exit()

if __name__ == "__main__":
    show_auth_menu()

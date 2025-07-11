from welcome import welcome_screen
from auth_menu import show_auth_menu
from register import register_user
from login import login_user
from rich.console import Console

console = Console()

def main():
    # Show welcome screen at startup
    welcome_screen()

    while True:
        action = show_auth_menu()

        if action == "register":
            register_user()
            console.input("\n[bold green]Press Enter to return to menu...[/bold green]")

        elif action == "login":
            result = login_user()
            if result:
                console.print(f"[bold cyan]Welcome, {result['name']}![/bold cyan]")
            console.input("\n[bold green]Press Enter to return to menu...[/bold green]")

if __name__ == "__main__":
    main()

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.panel import Panel
from rich.text import Text
from rich import box
import subprocess
import time

console = Console()

def scanning_animation(duration=10):
    dots = ["", ".", "..", "...", "...."]
    start_time = time.time()
    index = 0

    with Live(Align.center("", vertical="middle"), refresh_per_second=4) as live:
        while time.time() - start_time < duration:
            text = f"[bold cyan]🔍 Scanning local network{dots[index % len(dots)]}[/bold cyan]"
            live.update(Align.center(text, vertical="middle"))
            time.sleep(0.5)
            index += 1

def get_devices():
    try:
        # Show animation while scanning
        with Live(refresh_per_second=10) as live:
            dots = ["", ".", "..", "...", "...."]
            index = 0

            process = subprocess.Popen(['sudo', '../scanner'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output_lines = []

            while process.poll() is None:
                scan_text = f"[bold cyan]🔍 Scanning local network{dots[index % len(dots)]}[/bold cyan]"
                live.update(Align.center(scan_text, vertical="middle"))
                time.sleep(0.5)
                index += 1

            stdout, stderr = process.communicate()
            if process.returncode != 0:
                console.print(Align.center(f"[bold red]❌ Error:[/bold red] {stderr.strip()}"))
                return []

    except Exception as e:
        console.print(Align.center(f"[bold red]❌ Exception:[/bold red] {e}"))
        return []

    devices = []
    for line in stdout.splitlines():
        if "IP Address" in line:
            parts = line.strip().split(", ")
            ip = parts[0].split(": ")[1]
            hostname = parts[1].split(": ")[1]
            devices.append((ip, hostname))
    return devices

def show_table(devices):
    console.clear()

    # Header panel
    header = Panel.fit(
        "[bold blue]📡 Network Device Scanner[/bold blue]",
        border_style="green",
        padding=(0, 2)
    )
    console.print(Align.center(header))

    # Device info table
    table = Table(box=box.ROUNDED, border_style="bright_blue", title="[bold]🖥️   Detected Devices[/bold]")

    table.add_column("🔢 S.No", justify="center", style="bold white")
    table.add_column("🌐 IP Address", justify="center", style="cyan")
    table.add_column("🧭 Hostname", justify="center", style="magenta")

    for idx, (ip, hostname) in enumerate(devices, start=1):
        table.add_row(str(idx), ip, hostname)

    console.print(Align.center(table))

    # Footer panel
    if devices:
        footer = Panel.fit(
            f"[bold green]✅ Scan complete. Found {len(devices)} device(s).[/bold green] 🚀",
            border_style="green",
            padding=(0, 2)
        )
        console.print(Align.center(footer))

if __name__ == "__main__":
    devices = get_devices()
    if not devices:
        console.print(Align.center("[bold red]❌ No devices found on the network.[/bold red]"))
    else:
        show_table(devices)

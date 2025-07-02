import socket
import threading
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()
class ReceiverServiceBrowser:
    def __init__(self, service_type="_example._udp.local."):
        self.zeroconf = Zeroconf()
        self.service_type = service_type
        self.services = {}
        self.lock = threading.Lock()
        self.ready = threading.Event()

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                with self.lock:
                    self.services[name] = info
                self.ready.set()

    def discover(self, timeout=3):
        ServiceBrowser(self.zeroconf, self.service_type, handlers=[self.on_service_state_change])
        self.ready.wait(timeout)
        return self.services

def select_receiver(services: dict):
    console.clear()

    if not services:
        console.print(Align.center("[red]❌ No Zeroconf services found.[/red]"))
        return None

    console.print(Align.center(Panel.fit("[bold blue]📡 Zeroconf Receiver Discovery[/bold blue]", border_style="cyan")))

    table = Table(box=box.ROUNDED, border_style="blue", title="[bold]📋 Available Receivers[/bold]")
    table.add_column("🔢 Index", justify="center")
    table.add_column("📛 Name", justify="center", style="cyan")
    table.add_column("🌍 IP", justify="center", style="yellow")
    table.add_column("📦 Port", justify="center", style="green")
    table.add_column("📝 Info", justify="center", style="magenta")

    indexed = list(services.items())
    for i, (name, info) in enumerate(indexed):
        ip = socket.inet_ntoa(info.addresses[0])
        port = str(info.port)
        extra = info.properties.get(b"info", b"N/A").decode()
        table.add_row(str(i), name, ip, port, extra)

    console.print(table)
    console.print(Align.center(Panel.fit("[bold green]Enter the index of the receiver to use.[/bold green]")))

    while True:
        try:
            choice = int(console.input("[cyan]Select receiver index: [/cyan]").strip())
            return indexed[choice][1]
        except (ValueError, IndexError):
            console.print("[red]❌ Invalid selection. Try again.[/red]")

import socket
import threading
import time
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange, InterfaceChoice
from rich.console import Console, Group
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich import box

console = Console()

class ReceiverServiceBrowser:
    def __init__(self, service_type="_example._udp.local."):
        self.zeroconf = Zeroconf(interfaces=InterfaceChoice.All)
        self.service_type = service_type
        self.services = {}
        self.lock = threading.Lock()

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                with self.lock:
                    self.services[name] = info

    def discover(self, timeout=5):
        browser = ServiceBrowser(self.zeroconf, self.service_type, handlers=[self.on_service_state_change])

        with Live(self._render_table(), refresh_per_second=4) as live:
            for _ in range(timeout * 4):
                live.update(self._render_table())
                time.sleep(0.25)

        return self.services

    def _render_table(self):
        header = Panel.fit("[bold blue]📡 Discovering Zeroconf Receiver Services...[/bold blue]", border_style="cyan")

        table = Table(box=box.ROUNDED, border_style="blue", title="[bold]📋 Detected Receivers[/bold]")
        table.add_column("🔢 Index", justify="center")
        table.add_column("📛 Name", justify="center", style="cyan")
        table.add_column("🌍 IP", justify="center", style="yellow")
        table.add_column("📦 Port", justify="center", style="green")
        table.add_column("📝 Info", justify="center", style="magenta")

        with self.lock:
            for i, (name, info) in enumerate(self.services.items()):
                ip = socket.inet_ntoa(info.addresses[0]) if info.addresses else "?"
                port = str(info.port)
                extra = info.properties.get(b"info", b"N/A").decode()
                table.add_row(str(i), name, ip, port, extra)

        return Group(Align.center(header), Align.center(table))




def select_receiver(services):
    if not services:
        print("❌ No receivers found.")
        return []

    table = Table(title="Discovered Receivers")
    table.add_column("Index")
    table.add_column("Service Name")
    table.add_column("Address")
    table.add_column("Port")

    for i, (name, info) in enumerate(services.items()):
        addr = socket.inet_ntoa(info.addresses[0])
        table.add_row(str(i), info.name, addr, str(info.port))

    print(table)

    selected = Prompt.ask("Enter indices of receivers to select (comma separated)", default="0")
    indices = [int(i.strip()) for i in selected.split(',') if i.strip().isdigit()]
    indexed = list(services.items())
    return [info for i, (name, info) in enumerate(indexed) if i in indices]

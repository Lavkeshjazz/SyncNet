from scapy.all import ARP, Ether, srp
import socket
import ipaddress
import netifaces
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich.panel import Panel
from rich import box
import time

console = Console()

# 🌐 Reverse DNS
def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

# 🧠 Auto-detect subnet from default interface
def detect_subnet():
    try:
        gws = netifaces.gateways()
        default_iface = gws['default'][netifaces.AF_INET][1]
        iface_info = netifaces.ifaddresses(default_iface)[netifaces.AF_INET][0]
        ip = iface_info['addr']
        netmask = iface_info['netmask']
        cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))
        subnet = f"{ip}/{cidr}"
        return subnet
    except Exception as e:
        console.print(f"[red]❌ Auto-detect failed: {e}[/red]")
        return None

# 🔍 ARP Scan
def scan_network(subnet="192.168.1.0/24", timeout=5):
    ip_range = str(ipaddress.ip_network(subnet, strict=False))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=ip_range)
    packet = ether / arp
    result = srp(packet, timeout=timeout, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc,
            "hostname": get_hostname(received.psrc)
        })
    return devices

# 📊 Display results
def show_table(devices):
    console.clear()
    header = Panel.fit("[bold blue]📡 Network Device Scanner[/bold blue]", border_style="green")
    console.print(Align.center(header))

    table = Table(box=box.ROUNDED, border_style="bright_blue", title="[bold]🖥️   Detected Devices[/bold]")
    table.add_column("🔢 S.No", justify="center")
    table.add_column("🌐 IP Address", justify="center", style="cyan")
    table.add_column("💻 MAC Address", justify="center", style="yellow")
    table.add_column("🧭 Hostname", justify="center", style="magenta")

    for i, dev in enumerate(devices, 1):
        table.add_row(str(i), dev["ip"], dev["mac"], dev["hostname"])

    console.print(Align.center(table))

    if devices:
        console.print(Align.center(Panel.fit(f"[green]✅ Found {len(devices)} device(s).[/green] 🚀", border_style="green")))
    else:
        console.print(Align.center("[red]❌ No devices found on the network.[/red]"))

# 🧭 Ask user for subnet or detect automatically
def choose_subnet():
    console.print("\n[bold yellow]Choose scanning mode:[/bold yellow]")
    console.print("1️⃣  Auto-detect subnet from your PC")
    console.print("2️⃣  Manually enter a subnet (e.g., 192.168.1.0/24)")

    choice = console.input("\n[cyan]Enter choice (1 or 2): [/cyan]").strip()

    if choice == "1":
        subnet = detect_subnet()
        if not subnet:
            console.print("[red]Falling back to 192.168.1.0/24[/red]")
            subnet = "192.168.1.0/24"
    elif choice == "2":
        subnet = console.input("[cyan]Enter subnet (CIDR format): [/cyan]").strip()
    else:
        console.print("[red]Invalid choice. Defaulting to 192.168.1.0/24[/red]")
        subnet = "192.168.1.0/24"

    return subnet

# ▶️ Main
if __name__ == "__main__":
    subnet = choose_subnet()

    with Live(refresh_per_second=4) as live:
        dots = ["", ".", "..", "..."]
        for i in range(6):
            live.update(Align.center(f"[bold cyan]🔍 Scanning local network{dots[i % 4]}[/bold cyan]"))
            time.sleep(0.5)

    console.print(f"\n[cyan]🔍 Scanning subnet: {subnet}[/cyan]")
    devices = scan_network(subnet=subnet)
    show_table(devices)


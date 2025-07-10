import socket
import os
import struct
import time
import uuid
import threading
import selectors
from hashlib import blake2b
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import CHUNK_SIZE, METADATA_MAGIC
from ui_helpers import get_file_path
from discovery_ui import ReceiverServiceBrowser, select_receiver
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from helpers import get_current_ip

console = Console()

class SecureSender:
    def __init__(self):
        self.aes_key = os.urandom(32)
        self.iv_length = 16
        self.public_key = None
        self.repair_port = 10000
        self.mcast_group = '224.1.1.1'
        self.mcast_port = 5007
        self.sent_packets = {}
        self.receivers = []  # List of (ip, tcp_port)

    def tcp_key_exchange(self, ip, tcp_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, tcp_port))
        pem_data = b""
        while True:
            chunk = sock.recv(4096)
            pem_data += chunk
            if b"-----END PUBLIC KEY-----" in pem_data:
                break
        public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())
        encrypted_key = public_key.encrypt(
            self.aes_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        sock.sendall(encrypted_key)
        status = sock.recv(1024)
        if status.strip() != b"READY":
            console.print(f"[red]❌ Receiver at {ip}:{tcp_port} not ready[/red]")
            sock.close()
            return False
        group_name = "default_group"
        meta = f"{group_name},{self.mcast_group},{self.mcast_port}".encode()
        sock.sendall(meta)
        sock.close()
        return True

    def encrypt_packet(self, seq_num, message):
        iv = os.urandom(self.iv_length)
        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(message) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        checksum = blake2b(message, digest_size=32).digest()
        return seq_num.to_bytes(4, 'big') + iv + ciphertext + checksum

    def send_metadata(self, sock, multicast_ip, file_id, filename):
        file_id_bytes = file_id.encode()
        filename_bytes = os.path.basename(filename).encode()
        file_id_len = len(file_id_bytes)
        metadata_packet = METADATA_MAGIC + struct.pack(">H", file_id_len) + file_id_bytes + filename_bytes
        sock.sendto(metadata_packet, (multicast_ip, self.mcast_port))

    def chunk_file(self, filepath, chunk_size):
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def send_multicast(self, filepath):
        file_id = str(uuid.uuid4())
        filename = os.path.basename(filepath)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        self.send_metadata(sock, self.mcast_group, file_id, filename)
        console.print("📡 [cyan]Sending multicast packets...[/cyan]")
        for i, chunk in enumerate(self.chunk_file(filepath, CHUNK_SIZE)):
            header = struct.pack(">H", len(file_id.encode())) + file_id.encode() + struct.pack(">I", i)
            msg = header + chunk
            packet = self.encrypt_packet(i, msg)
            sock.sendto(packet, (self.mcast_group, self.mcast_port))
            self.sent_packets[i] = packet
            print(f"✅ Sent packet {i}")
            if i % 500 == 0:
                time.sleep(0.0001)  # Sleep for 10μs every 100 packets
        time.sleep(0.0001)
        sock.sendto(b"EOF", (self.mcast_group, self.mcast_port))
        sock.close()
        console.print("🛑 [green]EOF sent.[/green]")

    def handle_repair(self):
        sel = selectors.DefaultSelector()
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((get_current_ip(), self.repair_port))
        server_sock.listen()
        server_sock.setblocking(False)
        sel.register(server_sock, selectors.EVENT_READ, data=None)

        console.print(f"🔧 [yellow]Repair server listening on {get_current_ip()}:{self.repair_port}[/yellow]")

        def service_connection(key, mask):
            sock = key.fileobj
            addr = key.data["addr"]
            try:
                data = sock.recv(4096)
                if not data:
                    sel.unregister(sock)
                    sock.close()
                    return

                if data == b"COMPLETE":
                    console.print(f"✅ Receiver at {addr} completed transmission.")
                    sel.unregister(sock)
                    sock.close()
                    return

                missing = data.decode().split(',')
                console.print(f"🔁 [cyan]Resending {len(missing)} packets to {addr}[/cyan]")
                for m in missing:
                    try:
                        seq = int(m)
                        if seq in self.sent_packets:
                            sock.sendall(self.sent_packets[seq])
                            console.print(f"🔁 Resent packet {seq} to {addr}")
                    except Exception as e:
                        console.print(f"[red]❌ Failed to send packet {m} to {addr}: {e}[/red]")

                sel.unregister(sock)
                sock.close()
            except Exception as e:
                console.print(f"[red]❌ Error handling repair request from {addr}: {e}[/red]")
                sel.unregister(sock)
                sock.close()

        # Wait for repair requests for a fixed duration or until all are done
        timeout = time.time() + 10  # seconds
        while time.time() < timeout:
            events = sel.select(timeout=1)
            for key, mask in events:
                if key.data is None:
                    conn, addr = key.fileobj.accept()
                    conn.setblocking(False)
                    console.print(f"🔧 Repair connection from {addr}")
                    sel.register(conn, selectors.EVENT_READ, data={"addr": addr[0]})
                else:
                    service_connection(key, mask)

        sel.close()
        server_sock.close()
        console.print("[green]✅ Repair session ended[/green]")
    def run(self):
        console.print(Align.center(Panel.fit("[bold blue]🚀 Starting Secure Multicast Sender[/bold blue]")))

        browser = ReceiverServiceBrowser()
        services = browser.discover()
        selected = select_receiver(services)
        if not selected:
            return

        # Key exchange with all selected receivers
        for info in selected:
            ip = socket.inet_ntoa(info.addresses[0])
            port = info.port
            if self.tcp_key_exchange(ip, port):
                self.receivers.append(ip)

        if not self.receivers:
            console.print("[red]No receivers successfully initialized.[/red]")
            return

        file_path = get_file_path()
        self.send_multicast(file_path)
        self.handle_repair()
        print("🎉 Transmission completed successfully!")

if __name__ == "__main__":
    SecureSender().run()

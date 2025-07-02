# secure_sender.py
import socket
import os
import struct
import time
import uuid
from hashlib import blake2b
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from config import  CHUNK_SIZE, METADATA_MAGIC
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
        self.tcp_host = 'localhost'
        self.tcp_port = 9999
        self.repair_port = 10000
        self.mcast_group = '224.1.1.1'
        self.mcast_port = 5007
        self.sent_packets = {}  # Store packets by sequence number

    def tcp_key_exchange(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.tcp_host, self.tcp_port))
        pem_data = b""
        while True:
            chunk = sock.recv(4096)
            pem_data += chunk
            if b"-----END PUBLIC KEY-----" in pem_data:
                break
        self.public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())
        encrypted_key = self.public_key.encrypt(
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
            print("❌ Receiver not ready.")
            exit(1)
        group_name = "default_group"  # Replace with actual logic if needed
        meta = f"{group_name},{self.mcast_group},{self.mcast_port}".encode()
        sock.sendall(meta)
        sock.close()

    def encrypt_packet(self, seq_num, message):
        iv = os.urandom(self.iv_length)
        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(message) + padder.finalize()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        checksum = blake2b(message, digest_size=32).digest()
        return seq_num.to_bytes(4, 'big') + iv + ciphertext + checksum

    def send_metadata(self,sock, multicast_ip, file_id, filename):
        file_id_bytes = file_id.encode()
        filename_bytes = os.path.basename(filename).encode()
        file_id_len = len(file_id_bytes)
        metadata_packet = METADATA_MAGIC + struct.pack(">H", file_id_len) + file_id_bytes + filename_bytes
        sock.sendto(metadata_packet, (multicast_ip, self.mcast_port))

    def chunk_file(self,filepath, chunk_size):
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def send_multicast(self,filepath):
        # File Metadata
        file_id = str(uuid.uuid4())
        filename = os.path.basename(filepath)
        file_id_bytes = file_id.encode()
        file_id_len = len(file_id_bytes)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        self.send_metadata(sock, self.mcast_group, file_id, filename)
        print("📡 Sending multicast packets...")
        for i, chunk in enumerate(self.chunk_file(filepath, CHUNK_SIZE)):
            header = struct.pack(">H", file_id_len) + file_id_bytes + struct.pack(">I", i)
            msg = header + chunk
            packet = self.encrypt_packet(i, msg)
            sock.sendto(packet, (self.mcast_group, self.mcast_port))
            self.sent_packets[i] = packet  # Store for potential repair
            print(f"✅ Sent packet {i}")
            time.sleep(1)
        sock.sendto(b"EOF", (self.mcast_group, self.mcast_port))
        sock.close()
        print("🛑 Sent EOF")
        sock.close()

    def handle_repair(self):
        ip = get_current_ip()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ip, self.repair_port))
        sock.listen(1)
        print("🔧 Waiting for repair request...")
        
        conn, _ = sock.accept()
        request = conn.recv(1024)
        
        if request == b"COMPLETE":
            print("✅ Receiver confirmed all packets received successfully!")
            conn.close()
            sock.close()
            return
        
        # Handle missing packets
        missing = request.decode().split(',')
        print(f"🔁 Repairing missing packets: {missing}")
        for m in missing:
            seq = int(m)
            if seq in self.sent_packets:
                conn.sendall(self.sent_packets[seq])
                print(f"🔁 Resent packet {seq}")
        
        conn.close()
        sock.close()

    def run(self):
        console.print(Align.center(Panel.fit("[bold blue]🚀 Starting Secure Multicast Sender[/bold blue]")))

        # Step 1: Discover receivers via Zeroconf
        browser = ReceiverServiceBrowser()
        services = browser.discover()

        selected_info = select_receiver(services)
        if not selected_info:
            return

        # Step 2: Use selected receiver's IP and port
        self.tcp_host = socket.inet_ntoa(selected_info.addresses[0])
        self.tcp_port = selected_info.port
        print(self.tcp_port)
        print(self.tcp_host)

        self.tcp_key_exchange()

        # Step 3: Pick file to send
        from ui_helpers import get_file_path
        file_path = get_file_path()

        self.send_multicast(file_path)
        self.handle_repair()
        console.print(Align.center("[bold green]🎉 Transmission completed successfully![/bold green]"))

if __name__ == "__main__":
    SecureSender().run()

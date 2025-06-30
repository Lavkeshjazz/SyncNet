# secure_sender.py
import socket
import os
import struct
import time
from hashlib import blake2b
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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
        self.messages = [
            b"Hello from secure multicast!",
            b"This is message #2 - encrypted with AES-256",
            b"Message #3: Your data is protected.",
            b"Final message: End-to-end encryption working perfectly!"
        ]
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

    def send_multicast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
        print("📡 Sending multicast packets...")
        for i, msg in enumerate(self.messages, 1):
            packet = self.encrypt_packet(i, msg)
            sock.sendto(packet, (self.mcast_group, self.mcast_port))
            self.sent_packets[i] = packet  # Store for potential repair
            print(f"✅ Sent packet {i}")
            time.sleep(1)
        sock.sendto(b"EOF", (self.mcast_group, self.mcast_port))
        print("🛑 Sent EOF")
        sock.close()

    def handle_repair(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', self.repair_port))
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
        print("🚀 Starting Secure Multicast Sender")
        self.tcp_key_exchange()
        self.send_multicast()
        self.handle_repair()
        print("🎉 Transmission completed successfully!")

if __name__ == "__main__":
    SecureSender().run()
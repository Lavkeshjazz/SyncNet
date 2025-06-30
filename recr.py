# secure_receiver.py
import socket
import os
import struct
import threading
from hashlib import blake2b
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class SecureReceiver:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.aes_key = None
        self.tcp_port = 9999
        self.repair_port = 10000
        self.mcast_group = '224.1.1.1'
        self.mcast_port = 5007
        self.received_packets = {}  # seq_num: plaintext
        self.expected_total = 4  # Set expected message count

    def generate_rsa_keypair(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def tcp_handshake(self):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_sock.bind(('localhost', self.tcp_port))
        tcp_sock.listen(1)
        print("📥 Waiting for TCP connection...")
        conn, _ = tcp_sock.accept()
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        conn.sendall(pem)
        enc_key = conn.recv(1024)
        self.aes_key = self.private_key.decrypt(
            enc_key,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("✅ AES key derived.")
        conn.sendall(b"READY")
        conn.close()
        tcp_sock.close()

    def decrypt_message(self, packet):
        iv = packet[:16]
        ciphertext = packet[16:-32]
        hash_val = packet[-32:]

        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = sym_padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded) + unpadder.finalize()

        if blake2b(plaintext, digest_size=32).digest() != hash_val:
            return None
        return plaintext

    def listen_multicast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.mcast_port))
        mreq = struct.pack("4sl", socket.inet_aton(self.mcast_group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        print("📡 Listening for multicast messages...")
        while True:
            data, _ = sock.recvfrom(20480)
            if data == b"EOF":
                print("🛑 Transmission complete.")
                break
            seq_num = int.from_bytes(data[:4], 'big')
            packet = data[4:]
            msg = self.decrypt_message(packet)
            if msg:
                self.received_packets[seq_num] = msg
                print(f"✅ Message {seq_num}: {msg.decode()}")
            else:
                print(f"❌ Failed to decrypt message {seq_num}")
        sock.close()

    def request_missing(self):
        missing = [str(i) for i in range(1, self.expected_total+1) if i not in self.received_packets]
        
        # Always connect to sender to report status
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', self.repair_port))
        
        if not missing:
            print("✅ All packets received.")
            sock.sendall(b"COMPLETE")  # Signal no repair needed
            sock.close()
            return
        
        print(f"🔁 Requesting missing packets: {missing}")
        sock.sendall(','.join(missing).encode())
        
        while True:
            data = sock.recv(20480)
            if not data:
                break
            seq_num = int.from_bytes(data[:4], 'big')
            packet = data[4:]
            msg = self.decrypt_message(packet)
            if msg:
                print(f"🛠️ Recovered {seq_num}: {msg.decode()}")
                self.received_packets[seq_num] = msg
        sock.close()

    def run(self):
        self.generate_rsa_keypair()
        self.tcp_handshake()
        self.listen_multicast()
        self.request_missing()

if __name__ == "__main__":
    SecureReceiver().run()
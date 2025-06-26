import socket
import struct
import os
from hashlib import blake2b
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from constants import *

# Generate AES key and IV
key = os.urandom(KEY_SIZE)
iv = os.urandom(IV_SIZE)

# Send key and IV to receiver over TCP
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((TCP_IP, TCP_PORT))
tcp_sock.sendall(key)
tcp_sock.sendall(iv)
tcp_sock.close()
print("🔐 Key and IV sent.")

# Read file to send
with open("sample.txt", "rb") as f:
    data = f.read()

CHUNK_SIZE = 1024
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Send chunks via UDP multicast
for i in range(0, len(data), CHUNK_SIZE):
    chunk = data[i:i+CHUNK_SIZE]

    # Padding
    padder = padding.PKCS7(128).padder()
    padded = padder.update(chunk) + padder.finalize()

    # Encrypt with AES CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    # Blake2b integrity hash
    h = blake2b(chunk, digest_size=32).digest()

    # Packet format: [index][IV][ciphertext][hash]
    packet = i.to_bytes(4, 'big') + iv + ciphertext + h
    sock.sendto(packet, (MCAST_GRP, MCAST_PORT))

# EOF packet
sock.sendto(b"EOF", (MCAST_GRP, MCAST_PORT))
print("✅ File sent.")

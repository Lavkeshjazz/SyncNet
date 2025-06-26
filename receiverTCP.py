import socket
import struct
from hashlib import blake2b
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from constants import *

# Set up TCP socket to receive key and IV
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((TCP_IP, TCP_PORT))
tcp_sock.listen(1)
print("🔐 Waiting for key via TCP...")
conn, _ = tcp_sock.accept()
key = conn.recv(KEY_SIZE)
iv = conn.recv(IV_SIZE)
conn.close()
print("✅ Key and IV received.")

# Set up multicast UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))
mreq = struct.pack('4sL', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

chunks = {}
print("📥 Listening for multicast packets...")

while True:
    data, _ = sock.recvfrom(65536)
    if data == b"EOF":
        print("📦 Transmission complete.")
        break

    index = int.from_bytes(data[:4], 'big')
    iv_recv = data[4:20]
    ciphertext = data[20:-32]
    recv_hash = data[-32:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv_recv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    try:
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    except Exception:
        print(f"❌ Padding error at chunk {index}")
        continue

    calc_hash = blake2b(plaintext, digest_size=32).digest()
    if calc_hash != recv_hash:
        print(f"⚠️ Integrity check failed on chunk {index}")
    else:
        print(f"✅ Chunk {index} verified.")
        chunks[index] = plaintext

# Reconstruct full file
with open("reconstructed.txt", "wb") as f:
    for i in sorted(chunks.keys()):
        f.write(chunks[i])

print("✅ File successfully reconstructed!")

import socket
import os
import struct
from config import PORT, CHUNK_SIZE, METADATA_MAGIC

def send_metadata(sock, multicast_ip, file_id, filename):
    file_id_bytes = file_id.encode()
    filename_bytes = os.path.basename(filename).encode()
    file_id_len = len(file_id_bytes)
    metadata_packet = METADATA_MAGIC + struct.pack(">H", file_id_len) + file_id_bytes + filename_bytes
    sock.sendto(metadata_packet, (multicast_ip, PORT))

def send_file(file_id, filepath, multicast_ips):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        chunks = []
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)

    file_id_bytes = file_id.encode()
    file_id_len = len(file_id_bytes)

    for ip in multicast_ips:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        # Send metadata packet first
        send_metadata(sock, ip, file_id, filename)

        # Send file data
        for i, chunk in enumerate(chunks):
            header = struct.pack(">H", file_id_len) + file_id_bytes + struct.pack(">I", i)
            packet = header + chunk
            sock.sendto(packet, (ip, PORT))
        print(f"[✓] Sent file to {ip} with {len(chunks)} packets.")
        sock.close()

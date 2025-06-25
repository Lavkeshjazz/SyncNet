import socket
import struct
from assembler import write_packet, save_file, metadata_map
from config import PORT, BUFFER_SIZE, METADATA_MAGIC

def join_multicast(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', PORT))
    mreq = struct.pack("4sl", socket.inet_aton(ip), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def listen(sock):
    print(f"[*] Listening for packets on {sock.getsockname()}...")
    try:
        while True:
            packet, _ = sock.recvfrom(BUFFER_SIZE)
            if packet.startswith(METADATA_MAGIC):
                _, file_id_len = struct.unpack('>4sH', packet[:6])
                file_id = packet[6:6 + file_id_len].decode()
                filename = packet[6 + file_id_len:].decode()
                metadata_map[file_id] = filename
                print(f"[+] Received metadata: file_id={file_id}, filename={filename}")
            else:
                file_id_len = struct.unpack('>H', packet[:2])[0]
                file_id = packet[2:2 + file_id_len].decode()
                packet_no = struct.unpack('>I', packet[2 + file_id_len:6 + file_id_len])[0]
                data = packet[6 + file_id_len:]
                write_packet(file_id, packet_no, data)
    except KeyboardInterrupt:
        print("\n[!] Interrupted. Saving files...")
        for file_id in list(metadata_map):
            save_file(file_id)

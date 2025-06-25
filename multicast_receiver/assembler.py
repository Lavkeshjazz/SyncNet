import os
import threading
from collections import defaultdict

assembled_data = defaultdict(dict)
received_status = defaultdict(set)
locks = defaultdict(threading.Lock)

metadata_map = {}

def write_packet(file_id, packet_no, data):
    with locks[file_id]:
        assembled_data[file_id][packet_no] = data
        received_status[file_id].add(packet_no)

def save_file(file_id):
    with locks[file_id]:
        if not os.path.exists("received_files"):
            os.makedirs("received_files")
        filename = metadata_map.get(file_id, f"{file_id}.bin")
        file_path = os.path.join("received_files", filename)
        with open(file_path, 'wb') as f:
            for packet_no in sorted(assembled_data[file_id].keys()):
                f.write(assembled_data[file_id][packet_no])
        print(f"[✓] File saved: {file_path}")
        del assembled_data[file_id]
        del received_status[file_id]
        del locks[file_id]
        if file_id in metadata_map:
            del metadata_map[file_id]

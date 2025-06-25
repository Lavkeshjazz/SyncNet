from config import CHUNK_SIZE

def packetize(file_path):
    with open(file_path, 'rb') as f:
        packet_no = 0
        while chunk := f.read(CHUNK_SIZE):
            yield packet_no, chunk
            packet_no += 1

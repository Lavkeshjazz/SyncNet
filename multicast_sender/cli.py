import argparse
import uuid
from models import init_db
from sender import send_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multicast File Sender")
    parser.add_argument("--file", help="Path to the file to send")
    parser.add_argument("--ips", nargs='+', required=True, help="List of multicast IPs")
    args = parser.parse_args()

    init_db()
    file_id = str(uuid.uuid4())
    print(f"[INFO] Sending file with ID: {file_id}")
    send_file(file_id, args.file, args.ips)

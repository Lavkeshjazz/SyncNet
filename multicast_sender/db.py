import sqlite3
from config import DB_FILE

def store_packet(file_id, ip, packet_no, data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO packets (file_id, ip, packet_no, data)
        VALUES (?, ?, ?, ?)
    """, (file_id, ip, packet_no, data))
    conn.commit()
    conn.close()

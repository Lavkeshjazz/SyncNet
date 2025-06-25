import sqlite3
from config import DB_FILE

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            file_id TEXT,
            ip TEXT,
            packet_no INTEGER,
            data BLOB,
            PRIMARY KEY (file_id, ip, packet_no)
        )
    ''')
    conn.commit()
    conn.close()

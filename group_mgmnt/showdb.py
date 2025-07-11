import sqlite3

def inspect_db_structure(db_name="syncnet.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"📦 Tables in {db_name}:\n")
    for (table,) in tables:
        print(f"🔹 Table: {table}")
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        for col in columns:
            cid, name, datatype, notnull, default_value, pk = col
            print(f"   - {name} ({datatype}) {'PRIMARY KEY' if pk else ''}")
        print()

    conn.close()

if __name__ == "__main__":
    inspect_db_structure()

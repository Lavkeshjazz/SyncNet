import sqlite3

def populate_users_from_roles():
    conn = sqlite3.connect("syncnet.db")
    cursor = conn.cursor()

    # Ensure Users table exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        ip_address TEXT,
        date_of_joining TEXT
    )
    """)

    # Collect users from all three roles
    roles = [
        ("Suppliers", "supplier_name", "user_id", "ip_address", "date_of_joining"),
        ("Warehouses", "warehouse_name", "user_id", "ip_address", "date_of_joining"),
        ("RegionalHubs", "hub_name", "user_id", "ip_address", "date_of_establishment")
    ]

    inserted = 0
    for table, name_col, user_id_col, ip_col, date_col in roles:
        cursor.execute(f"SELECT {user_id_col}, {name_col}, {ip_col}, {date_col} FROM {table}")
        for user_id, name, ip, join_date in cursor.fetchall():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO Users (user_id, name, ip_address, date_of_joining)
                    VALUES (?, ?, ?, ?)
                """, (user_id, name, ip, join_date))
                inserted += 1
            except Exception as e:
                print(f"⚠️ Skipped user {user_id}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Populated Users table with {inserted} entries.")

if __name__ == "__main__":
    populate_users_from_roles()

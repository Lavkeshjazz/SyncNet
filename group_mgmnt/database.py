import sqlite3

def create_tables():
    conn = sqlite3.connect("syncnet.db")  # Creates or connects to syncnet.db
    cursor = conn.cursor()

    # Regional Hubs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS RegionalHubs (
            hub_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hub_name TEXT NOT NULL,
            location TEXT NOT NULL,
            contact_number TEXT,
            date_of_establishment DATE
        )
    ''')

    # Warehouses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Warehouses (
            warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_name TEXT NOT NULL,
            location TEXT NOT NULL,
            contact_number TEXT,
            hub_id INTEGER,
            orders_sent INTEGER DEFAULT 0,
            date_of_joining DATE,
            FOREIGN KEY (hub_id) REFERENCES RegionalHubs(hub_id)
        )
    ''')

    # Suppliers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_name TEXT NOT NULL,
            contact_number TEXT,
            orders_received INTEGER DEFAULT 0,
            date_of_joining DATE
        )
    ''')

    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            order_date DATE DEFAULT (DATE('now')),
            item_description TEXT,
            quantity INTEGER,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id),
            FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized and tables created.")

if __name__ == "__main__":
    create_tables()

import sqlite3

def clear_all_data(db_name="syncnet.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # List of all tables whose data you want to delete
    tables = ["Orders", "Suppliers", "Warehouses", "RegionalHubs"]

    try:
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            print(f"🧹 Cleared data from table: {table}")

        conn.commit()
        print("✅ All specified table data has been deleted.")
    except Exception as e:
        print(f"❌ Error while clearing data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_all_data()

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('search_llm.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables created in search_llm.db:")
for table in tables:
    print(f"  - {table[0]}")

# Get schema for first few tables
print("\nTable schemas:")
for table in tables[:3]:  # Show first 3 tables
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n{table_name}:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()
print("\nDatabase successfully created and ready to use!")
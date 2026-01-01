"""
Temporary script to run database migration
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")

# Read migration script
with open("migrations/001_add_chat_tables.sql", "r") as f:
    migration_sql = f.read()

# Connect and run migration
print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("Running migration...")
try:
    cursor.execute(migration_sql)
    print("SUCCESS: Migration completed successfully!")
    print("   - Created conversations table with indexes")
    print("   - Created messages table with indexes")
    print("   - Created update_conversation_timestamp trigger")
except Exception as e:
    print(f"ERROR: Migration failed: {e}")
    raise
finally:
    cursor.close()
    conn.close()

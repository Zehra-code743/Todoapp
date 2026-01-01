"""
Verify database migration tables exist
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Check conversations table
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'conversations'
    ORDER BY ordinal_position;
""")
conversations_cols = cursor.fetchall()

# Check messages table
cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'messages'
    ORDER BY ordinal_position;
""")
messages_cols = cursor.fetchall()

# Check trigger
cursor.execute("""
    SELECT trigger_name
    FROM information_schema.triggers
    WHERE trigger_name = 'trigger_update_conversation_timestamp';
""")
trigger = cursor.fetchone()

print("MIGRATION VERIFICATION REPORT")
print("=" * 50)
print("\nConversations table columns:")
for col in conversations_cols:
    print(f"  - {col[0]}: {col[1]}")

print("\nMessages table columns:")
for col in messages_cols:
    print(f"  - {col[0]}: {col[1]}")

print(f"\nTrigger: {trigger[0] if trigger else 'NOT FOUND'}")

if conversations_cols and messages_cols and trigger:
    print("\nSTATUS: Migration successful - all tables and triggers created")
else:
    print("\nSTATUS: Migration incomplete - missing objects")

cursor.close()
conn.close()

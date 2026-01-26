"""Add ai_daily_limit column to users table if it doesn't exist."""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent / "wos.db"
print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute('PRAGMA table_info(users)')
columns = [col[1] for col in cursor.fetchall()]
print(f"Existing columns: {columns}")

if 'ai_daily_limit' not in columns:
    print("Adding ai_daily_limit column...")
    cursor.execute('ALTER TABLE users ADD COLUMN ai_daily_limit INTEGER')
    conn.commit()
    print("Column added successfully!")
else:
    print("Column already exists")

conn.close()

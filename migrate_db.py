"""Simple SQLite migration script.

This script creates a timestamped backup of `websites.db` (if present) and
adds the `created_by` TEXT column to the `websites` table if it doesn't exist.
Run: python migrate_db.py
"""
import os
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "websites.db")


def backup_db(db_path: str) -> str:
    if not os.path.exists(db_path):
        return ""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup = f"{db_path}.backup.{ts}"
    shutil.copy2(db_path, backup)
    return backup


def ensure_column_created_by(db_path: str) -> bool:
    if not os.path.exists(db_path):
        print("No DB file found; nothing to migrate.")
        return False
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(websites)")
        cols = [r[1] for r in cur.fetchall()]
        if 'created_by' in cols:
            print("Column 'created_by' already exists.")
            return True
        print("Adding column 'created_by' to websites table...")
        cur.execute("ALTER TABLE websites ADD COLUMN created_by TEXT")
        conn.commit()
        print("Column added.")
        return True
    except sqlite3.OperationalError as e:
        print("SQLite error during migration:", e)
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    backup = backup_db(DB_PATH)
    if backup:
        print(f"Backup created: {backup}")
    ok = ensure_column_created_by(DB_PATH)
    if ok:
        print("Migration complete.")
    else:
        print("Migration failed or nothing to do.")

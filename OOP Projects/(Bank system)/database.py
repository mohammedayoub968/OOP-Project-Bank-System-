# database.py
import sqlite3

conn = sqlite3.connect("banking.db", check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            national_id TEXT UNIQUE,
            phone_number TEXT,
            password TEXT,
            is_locked INTEGER DEFAULT 0,
            user_type TEXT CHECK(user_type IN ('admin', 'customer'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            credit REAL DEFAULT 0.0,
            wallet_balance REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount REAL,
            status TEXT,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

__all__ = ["conn", "cursor", "create_tables"]

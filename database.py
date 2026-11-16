
import sqlite3

def init_db():
    connection = sqlite3.connect("users.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            voice_file TEXT
        )
    """)

    connection.commit()
    connection.close()

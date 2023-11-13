import sqlite3 as sl
db = sl.connect('deitabeiza.db')

db.execute('''
                CREATE TABLE IF NOT EXISTS __(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                value INTEGER,
                float REAL)
                ''')


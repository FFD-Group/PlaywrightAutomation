from flask import g

import sqlite3

DATABASE = "suppliers.sqlite"

def create_database() -> None:
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY,
        name VARCHAR,
        download_type VARCHAR,
        download_url VARCHAR,
        file_type VARCHAR,
        download_path VARCHAR
        ''')
    conn.commit()
    conn.close()

def get_db() -> sqlite3.Connection:
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False) -> sqlite3.Row|str|None:
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
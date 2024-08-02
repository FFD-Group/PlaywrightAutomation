from typing import List
from flask import g

import sqlite3

DATABASE = "suppliers.sqlite"

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

def insert_to_db(query, args=()) -> int|None:
    db = get_db()
    cur = db.cursor().execute(query, args)
    result = cur.lastrowid
    db.commit()
    return result
    
def delete_from_db(query, args=(), returning=None) -> List[str]|str|None:
    query = f"{query} RETURNING {returning}" if returning else query
    db = get_db()
    cur = db.cursor().execute(query, args).fetchall()
    db.commit()
    return cur if returning else None

    

from __future__ import annotations
import hashlib, json, sqlite3, os, time
from typing import Any, Optional

DB = os.path.expanduser('~/.cache/toscheck/index.sqlite3')
os.makedirs(os.path.dirname(DB), exist_ok=True)

def _db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS items(
        key TEXT PRIMARY KEY, value TEXT, ts REAL
    )""")
    return con

def _key(kind: str, text: str) -> str:
    return f"{kind}:" + hashlib.sha1(text.encode("utf-8")).hexdigest()

def get(kind: str, text: str) -> Optional[Any]:
    con = _db()
    k = _key(kind, text)
    row = con.execute("SELECT value FROM items WHERE key=?", (k,)).fetchone()
    return json.loads(row[0]) if row else None

def put(kind: str, text: str, value: Any) -> None:
    con = _db()
    k = _key(kind, text)
    con.execute("INSERT OR REPLACE INTO items(key,value,ts) VALUES(?,?,?)",
                (k, json.dumps(value), time.time()))
    con.commit()

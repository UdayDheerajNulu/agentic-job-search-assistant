"""SQLite application tracker."""
import os
import sqlite3
import time

DB_PATH = os.getenv("JOBS_DB", os.path.join(os.path.dirname(os.path.dirname(__file__)), "jobs.db"))
STATUSES = ["saved", "applied", "interview", "offer", "rejected"]

_SCHEMA = """CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT, company TEXT, location TEXT, score INTEGER,
  status TEXT DEFAULT 'saved', source TEXT, url TEXT, jd_text TEXT, notes TEXT,
  created_at REAL, updated_at REAL
);"""


def _conn(path=None):
    c = sqlite3.connect(path or DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db(path=None):
    with _conn(path) as c:
        c.execute(_SCHEMA)


def add_job(d, path=None):
    init_db(path)
    now = time.time()
    with _conn(path) as c:
        cur = c.execute(
            "INSERT INTO jobs (title, company, location, score, status, source, url, jd_text, notes, created_at, updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (d.get("title"), d.get("company"), d.get("location"), d.get("score"),
             d.get("status", "saved"), d.get("source"), d.get("url"),
             d.get("jd_text"), d.get("notes"), now, now),
        )
        return cur.lastrowid


def update_status(job_id, status, path=None):
    with _conn(path) as c:
        c.execute("UPDATE jobs SET status=?, updated_at=? WHERE id=?", (status, time.time(), job_id))


def list_jobs(path=None):
    init_db(path)
    with _conn(path) as c:
        return [dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY score DESC, updated_at DESC")]

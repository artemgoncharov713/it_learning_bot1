import sqlite3
from contextlib import contextmanager
from config import DB_PATH


@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.create_function("py_lower", 1, lambda s: s.lower() if isinstance(s, str) else s)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_connection():
    """Обычное соединение (для мест, где нельзя использовать with)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            name TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            material_type TEXT NOT NULL,
            link TEXT NOT NULL,
            description TEXT,
            video_link TEXT,
            file_id TEXT);
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL REFERENCES materials(id) ON DELETE CASCADE,
            UNIQUE (telegram_id, material_id));
        """)


# ============================================================
# SUBJECTS
# ============================================================

def get_subjects():
    with db() as conn:
        return conn.execute("SELECT * FROM subjects ORDER BY name").fetchall()


def add_subject(name: str):
    with db() as conn:
        conn.execute("INSERT INTO subjects (name) VALUES (?)", (name,))


def update_subject(subject_id: int, name: str):
    with db() as conn:
        conn.execute("UPDATE subjects SET name = ? WHERE id = ?", (name, subject_id))


def delete_subject(subject_id: int):
    with db() as conn:
        conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))


# ============================================================
# TOPICS
# ============================================================

def get_topics(subject_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM topics WHERE subject_id = ? ORDER BY name",
            (subject_id,)
        ).fetchall()


def add_topic(subject_id: int, name: str):
    with db() as conn:
        conn.execute(
            "INSERT INTO topics (subject_id, name) VALUES (?, ?)",
            (subject_id, name)
        )


def update_topic(topic_id: int, name: str):
    with db() as conn:
        conn.execute("UPDATE topics SET name = ? WHERE id = ?", (name, topic_id))


def delete_topic(topic_id: int):
    with db() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))


# ============================================================
# MATERIALS
# ============================================================

def get_materials(topic_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM materials WHERE topic_id = ? ORDER BY name",
            (topic_id,)
        ).fetchall()


def get_material(material_id: int):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM materials WHERE id = ?", (material_id,)
        ).fetchone()


def add_material(topic_id, name, material_type, link,
                 description=None, video_link=None, file_id=None):
    with db() as conn:
        conn.execute(
            """INSERT INTO materials
               (topic_id, name, material_type, link, description, video_link, file_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (topic_id, name, material_type, link,
             description, video_link, file_id)
        )


def update_material(material_id: int, field: str, value):
    allowed = {"name", "material_type", "link", "description", "video_link", "file_id"}
    if field not in allowed:
        raise ValueError(f"Недопустимое поле: {field}")
    with db() as conn:
        conn.execute(
            f"UPDATE materials SET {field} = ? WHERE id = ?",
            (value, material_id)
        )


def delete_material(material_id: int):
    with db() as conn:
        conn.execute("DELETE FROM materials WHERE id = ?", (material_id,))


# ============================================================
# SEARCH
# ============================================================

def search_materials(query: str):
    q = (query.strip().lower()
         .replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_"))
    p = f"%{q}%"
    with db() as conn:
        return conn.execute(
            """SELECT id, name, material_type, link, description, video_link, file_id
               FROM materials
               WHERE py_lower(name) LIKE ? ESCAPE '\\'
                  OR py_lower(COALESCE(description, '')) LIKE ? ESCAPE '\\'
               ORDER BY name""", (p, p)).fetchall()


# ============================================================
# FAVORITES
# ============================================================

def add_to_favorites(telegram_id: int, material_id: int) -> bool:
    with db() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO favorites (telegram_id, material_id) VALUES (?, ?)",
            (telegram_id, material_id)
        )
        return cur.rowcount > 0


def get_favorites(telegram_id: int):
    with db() as conn:
        return conn.execute(
            """SELECT m.id, m.name, m.material_type, m.link,
                      m.description, m.video_link, m.file_id
               FROM favorites f
               JOIN materials m ON m.id = f.material_id
               WHERE f.telegram_id = ?
               ORDER BY m.name""",
            (telegram_id,)
        ).fetchall()


def remove_from_favorites(telegram_id: int, material_id: int) -> bool:
    with db() as conn:
        cur = conn.execute(
            "DELETE FROM favorites WHERE telegram_id = ? AND material_id = ?",
            (telegram_id, material_id)
        )
        return cur.rowcount > 0
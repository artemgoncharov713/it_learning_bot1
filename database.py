import sqlite3
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


# ---------- Каталог ----------

def get_subjects():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name FROM subjects ORDER BY name"
        ).fetchall()


def get_topics(subject_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name FROM topics WHERE subject_id = ? ORDER BY name",
            (subject_id,)
        ).fetchall()


def get_materials(topic_id: int):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, material_type, link, description 
            FROM materials 
            WHERE topic_id = ? 
            ORDER BY name
            """,
            (topic_id,)
        ).fetchall()


def get_material(material_id: int):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, material_type, link, description 
            FROM materials 
            WHERE id = ?
            """,
            (material_id,)
        ).fetchone()


# ---------- Поиск ----------

def search_materials(query: str):
    with get_connection() as conn:
        pattern = f"%{query}%"
        return conn.execute(
            """
            SELECT id, name, material_type, link, description 
            FROM materials 
            WHERE name LIKE ? 
            ORDER BY name
            """,
            (pattern,)
        ).fetchall()


# ---------- Избранное ----------

def add_to_favorites(telegram_id: int, material_id: int) -> bool:
    """True — добавлено, False — уже было."""
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO favorites (telegram_id, material_id) VALUES (?, ?)",
                (telegram_id, material_id)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_favorites(telegram_id: int):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT m.id, m.name, m.material_type, m.link, m.description 
            FROM favorites f 
            JOIN materials m ON m.id = f.material_id 
            WHERE f.telegram_id = ? 
            ORDER BY f.id DESC
            """,
            (telegram_id,)
        ).fetchall()


def remove_from_favorites(telegram_id: int, material_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM favorites WHERE telegram_id = ? AND material_id = ?",
            (telegram_id, material_id)
        )
        conn.commit()
        return cur.rowcount > 0
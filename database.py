import sqlite3

from config import DB_PATH


# ============================================================
# ПОДКЛЮЧЕНИЕ
# ============================================================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# КАТАЛОГ
# ============================================================

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
            """SELECT id, name, material_type, link, description, video_link
               FROM materials WHERE topic_id = ? ORDER BY name""",
            (topic_id,)
        ).fetchall()


def get_material(material_id: int):
    with get_connection() as conn:
        return conn.execute(
            """SELECT id, name, material_type, link, description, video_link
               FROM materials WHERE id = ?""",
            (material_id,)
        ).fetchone()


def get_subject(subject_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name FROM subjects WHERE id = ?",
            (subject_id,)
        ).fetchone()


def get_topic(topic_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, subject_id, name FROM topics WHERE id = ?",
            (topic_id,)
        ).fetchone()


# ============================================================
# ПОИСК
# ============================================================

def search_materials(query: str):
    with get_connection() as conn:
        pattern = f"%{query}%"
        return conn.execute(
            """SELECT id, name, material_type, link, description, video_link
               FROM materials WHERE name LIKE ? ORDER BY name""",
            (pattern,)
        ).fetchall()


# ============================================================
# ИЗБРАННОЕ
# ============================================================

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
            """SELECT m.id, m.name, m.material_type, m.link,
                      m.description, m.video_link
               FROM favorites f
               JOIN materials m ON m.id = f.material_id
               WHERE f.telegram_id = ?
               ORDER BY f.id DESC""",
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


# ============================================================
# ДИСЦИПЛИНЫ: add / update / delete (админ)
# ============================================================

def add_subject(name: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO subjects (name) VALUES (?)", (name,)
        )
        conn.commit()
        return cur.lastrowid


def update_subject(subject_id: int, name: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE subjects SET name = ? WHERE id = ?",
            (name, subject_id)
        )
        conn.commit()
        return cur.rowcount > 0


def delete_subject(subject_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM subjects WHERE id = ?", (subject_id,)
        )
        conn.commit()
        return cur.rowcount > 0


# ============================================================
# ТЕМЫ: add / update / delete (админ)
# ============================================================

def add_topic(subject_id: int, name: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO topics (subject_id, name) VALUES (?, ?)",
            (subject_id, name)
        )
        conn.commit()
        return cur.lastrowid


def update_topic(topic_id: int, name: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE topics SET name = ? WHERE id = ?",
            (name, topic_id)
        )
        conn.commit()
        return cur.rowcount > 0


def delete_topic(topic_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM topics WHERE id = ?", (topic_id,)
        )
        conn.commit()
        return cur.rowcount > 0


# ============================================================
# МАТЕРИАЛЫ: add / update / delete (админ)
# ============================================================

def add_material(
    topic_id: int,
    name: str,
    material_type: str,
    link: str,
    description: str = None,
    video_link: str = None
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO materials
               (topic_id, name, material_type, link, description, video_link)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (topic_id, name, material_type, link, description, video_link)
        )
        conn.commit()
        return cur.lastrowid


def update_material(material_id: int, field: str, value) -> bool:
    """Обновляет одно поле материала. field — имя колонки."""
    allowed = {"name", "material_type", "link", "description", "video_link"}
    if field not in allowed:
        raise ValueError(f"Недопустимое поле: {field}")

    with get_connection() as conn:
        cur = conn.execute(
            f"UPDATE materials SET {field} = ? WHERE id = ?",
            (value, material_id)
        )
        conn.commit()
        return cur.rowcount > 0


def delete_material(material_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "DELETE FROM materials WHERE id = ?", (material_id,)
        )
        conn.commit()
        return cur.rowcount > 0
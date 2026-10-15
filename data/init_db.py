import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topics (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    name       TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS materials (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id      INTEGER NOT NULL,
    name          TEXT NOT NULL,
    material_type TEXT NOT NULL,
    link          TEXT NOT NULL,
    description   TEXT,
    video_link    TEXT,
    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS favorites (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE,
    UNIQUE (telegram_id, material_id)
);
"""


DEMO_DATA = {
    "Основы Python": {
        "Введение в Python": [
            ("Установка Python и настройка окружения", "теория",
             "https://docs.python.org/3/using/index.html",
             "Как установить интерпретатор и подготовить рабочее место.",
             "https://t.me/IT_snrg/2"),
            ("Первая программа Hello, World", "примеры кода",
             "https://docs.python.org/3/tutorial/introduction.html",
             "Минимальный пример запуска программы.",
             None),
        ],
        "Типы данных": [
            ("Числа и строки", "теория",
             "https://docs.python.org/3/tutorial/introduction.html#numbers",
             "Основные встроенные типы данных Python.",
             "https://t.me/IT_snrg/3"),
            ("Примеры работы со списками", "примеры кода",
             "https://docs.python.org/3/tutorial/datastructures.html",
             "Создание, изменение и обход списков.",
             None),
        ],
        "Условия и циклы": [
            ("Оператор if и его формы", "теория",
             "https://docs.python.org/3/tutorial/controlflow.html",
             "Как работают условия в Python.",
             None),
            ("Практика: циклы for и while", "практические задания",
             "https://docs.python.org/3/tutorial/controlflow.html#for-statements",
             "Набор задач на закрепление циклов.",
             None),
        ],
    },
    "Базы данных": {
        "Введение в базы данных": [
            ("Что такое СУБД", "теория",
             "https://ru.wikipedia.org/wiki/СУБД",
             "Основные понятия и назначение СУБД.",
             None),
            ("Установка SQLite", "теория",
             "https://www.sqlite.org/quickstart.html",
             "Быстрый старт работы с SQLite.",
             None),
        ],
        "SQL-запросы": [
            ("SELECT: выборка данных", "теория",
             "https://www.sqlite.org/lang_select.html",
             "Синтаксис и примеры SELECT.",
             None),
            ("Практика: JOIN-запросы", "практические задания",
             "https://www.sqlite.org/lang_select.html#join",
             "Соединение таблиц на примерах.",
             None),
        ],
        "Работа с Python и SQLite": [
            ("Модуль sqlite3", "примеры кода",
             "https://docs.python.org/3/library/sqlite3.html",
             "Подключение и выполнение запросов из Python.",
             None),
            ("Параметризованные запросы", "дополнительный материал",
             "https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders",
             "Как безопасно передавать данные в SQL.",
             None),
        ],
    },
    "Алгоритмы и структуры данных": {
        "Базовые структуры данных": [
            ("Массивы и списки", "теория",
             "https://ru.wikipedia.org/wiki/Массив_(структура_данных)",
             "Понятие массива и его применение.",
             None),
            ("Стек и очередь", "теория",
             "https://ru.wikipedia.org/wiki/Стек",
             "Основные абстрактные структуры данных.",
             None),
        ],
        "Сортировка и поиск": [
            ("Алгоритмы сортировки", "теория",
             "https://ru.wikipedia.org/wiki/Алгоритм_сортировки",
             "Обзор популярных алгоритмов сортировки.",
             None),
            ("Бинарный поиск: примеры", "примеры кода",
             "https://ru.wikipedia.org/wiki/Двоичный_поиск",
             "Реализация и разбор бинарного поиска.",
             None),
        ],
        "Сложность алгоритмов": [
            ("Big O нотация", "теория",
             "https://ru.wikipedia.org/wiki/«O»_большое",
             "Как оценивать сложность алгоритмов.",
             None),
            ("Практика: оценка сложности", "практические задания",
             "https://www.bigocheatsheet.com/",
             "Задачи на определение сложности.",
             None),
        ],
    },
}


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)

    count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    if count > 0:
        print("База уже заполнена.")
        conn.close()
        return

    for subject_name, topics in DEMO_DATA.items():
        cur = conn.execute(
            "INSERT INTO subjects (name) VALUES (?)", (subject_name,)
        )
        subject_id = cur.lastrowid

        for topic_name, materials in topics.items():
            cur = conn.execute(
                "INSERT INTO topics (subject_id, name) VALUES (?, ?)",
                (subject_id, topic_name)
            )
            topic_id = cur.lastrowid

            for name, mtype, link, descr, video in materials:
                conn.execute(
                    """INSERT INTO materials
                       (topic_id, name, material_type, link, description, video_link)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (topic_id, name, mtype, link, descr, video)
                )

    conn.commit()
    conn.close()
    print("База создана и заполнена демо-данными.")


if __name__ == "__main__":
    init_db()
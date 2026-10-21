import sqlite3
from datetime import datetime

DB_NAME = "studyflow.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            subject TEXT NOT NULL,
            deadline TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def add_task(task, subject, deadline=""):
    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks
        (task, subject, deadline, completed, created_at)
        VALUES (?, ?, ?, 0, ?)
        """,
        (
            task,
            subject,
            deadline,
            datetime.now().isoformat(),
        ),
    )

    task_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return task_id


def get_tasks():
    connection = get_connection()

    tasks = connection.execute(
        """
        SELECT id, task, subject, deadline, completed, created_at
        FROM tasks
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(task) for task in tasks]


def complete_task(task_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task_id,),
    )

    connection.commit()
    updated = cursor.rowcount
    connection.close()

    return updated > 0


initialize_database()

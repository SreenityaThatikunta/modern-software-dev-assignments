from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os
from pathlib import Path
import sqlite3
from typing import Iterator, Optional


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("ACTION_ITEMS_DB_PATH", str(DATA_DIR / "app.db")))


@dataclass(frozen=True)
class NoteRecord:
    id: int
    content: str
    created_at: str


@dataclass(frozen=True)
class ActionItemRecord:
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


def ensure_data_directory_exists() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection and always close it after its transaction."""
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def _note_from_row(row: sqlite3.Row) -> NoteRecord:
    return NoteRecord(id=row["id"], content=row["content"], created_at=row["created_at"])


def _action_item_from_row(row: sqlite3.Row) -> ActionItemRecord:
    return ActionItemRecord(
        id=row["id"],
        note_id=row["note_id"],
        text=row["text"],
        done=bool(row["done"]),
        created_at=row["created_at"],
    )


def init_db() -> None:
    ensure_data_directory_exists()
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )


def insert_note(content: str) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        return int(cursor.lastrowid)


def list_notes() -> list[NoteRecord]:
    with get_connection() as connection:
        rows = connection.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return [_note_from_row(row) for row in rows]


def get_note(note_id: int) -> Optional[NoteRecord]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        return _note_from_row(row) if row else None


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    with get_connection() as connection:
        cursor = connection.cursor()
        ids: list[int] = []
        for item in items:
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[ActionItemRecord]:
    with get_connection() as connection:
        if note_id is None:
            rows = connection.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:
            rows = connection.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return [_action_item_from_row(row) for row in rows]


def mark_action_item_done(action_item_id: int, done: bool) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        return cursor.rowcount == 1

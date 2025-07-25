#!/usr/bin/env python
import sqlite3
from decouple import config

DATABASE_URL = config("DATABASE_URL", default="sqlite:///./app.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        upload_url TEXT,
        transcript TEXT,
        hls_playlist_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        view_type TEXT NOT NULL,
        question TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER NOT NULL,
        view_type TEXT NOT NULL,
        prompt_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE,
        FOREIGN KEY (prompt_id) REFERENCES prompts (id),
        UNIQUE(video_id, prompt_id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
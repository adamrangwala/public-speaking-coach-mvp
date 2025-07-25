import sqlite3
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_connection, create_tables

def seed_prompts():
    """Seed the database with initial prompts for each view."""
    # First, ensure tables exist
    create_tables()

    prompts = [
        # Video Prompts (Body Language)
        ('video', 'How do you use your hands?',  1),
        ('video', 'Is there a purpose to how you move?', 2),
        ('video', 'What are your facial expressions like?', 3),
        ('video', 'Additional notes?', 4),

        # Audio Prompts (Voice & Tone)
        ('audio', 'What do you like about it?', 1),
        ('audio', 'Did I use vocal variety (pitch, volume, tone) effectively?', 2),
        ('audio', 'What did I not like about it?', 3),
        ('audio', 'Additional notes?', 4),

        # Text Prompts (Content & Structure)
        ('text', 'Are you using a lot of filler words?', 1),
        ('text', 'Are you using ahs and uhms?', 2),
        ('text', 'How intentional is your word choice?', 3),
        ('text', 'Additional notes?', 4)
    ]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if prompts already exist to avoid duplicates
        cursor.execute("SELECT COUNT(*) FROM prompts")
        if cursor.fetchone()[0] > 0:
            print("Prompts table is not empty. Skipping seed.")
            return

        cursor.executemany(
            "INSERT INTO prompts (view_type, question, order_index) VALUES (?, ?, ?)",
            prompts
        )
        conn.commit()
        print(f"Successfully inserted {len(prompts)} prompts.")
    except sqlite3.Error as e:
        print(f"Database error during seeding: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Seeding prompts into the database...")
    seed_prompts()
    print("Seeding complete.")
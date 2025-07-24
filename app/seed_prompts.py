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
        ('video', 'How was my posture and stance throughout the presentation?', 1),
        ('video', 'Were my gestures natural and supportive of my message?', 2),
        ('video', 'Did my facial expressions align with the content I was delivering?', 3),

        # Audio Prompts (Voice & Tone)
        ('audio', 'Was my pace of speaking appropriate? Too fast or too slow?', 1),
        ('audio', 'Did I use vocal variety (pitch, volume, tone) effectively?', 2),
        ('audio', 'How was my use of filler words (um, ah, like)?', 3),

        # Text Prompts (Content & Structure)
        ('text', 'Was the opening engaging and the closing memorable?', 1),
        ('text', 'Was the core message clear and easy to understand?', 2),
        ('text', 'How was the overall structure and flow of the content?', 3),
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
import os
import sys

# Add the app directory to the Python path

from app.database import create_tables
from app.seed_prompts import seed_prompts

UPLOADS_DIR = "uploads"
HLS_PLAYLIST_DIR = "hls_playlists"

def initialize_app():
    """
    Initializes the database, seeds it with prompts, and creates necessary directories.
    """
    print("--- Starting Application Initialization ---")

    try:
        print("Creating database tables...")
        create_tables()
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

    try:
        print("Seeding prompts...")
        seed_prompts()
        print("Prompts seeded successfully.")
    except Exception as e:
        print(f"Error seeding prompts: {e}")
        sys.exit(1)

    for directory in [UPLOADS_DIR, HLS_PLAYLIST_DIR]:
        try:
            if not os.path.exists(directory):
                print(f"Creating directory: {directory}")
                os.makedirs(directory)
                print(f"Directory '{directory}' created successfully.")
            else:
                print(f"Directory '{directory}' already exists.")
        except Exception as e:
            print(f"Error creating directory '{directory}': {e}")
            sys.exit(1)

    print("--- Application Initialization Complete ---")

if __name__ == "__main__":
    initialize_app()
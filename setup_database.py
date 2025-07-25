import os
import sys

# Add the app directory to the Python path

from app.database import create_tables
from app.seed_prompts import seed_prompts

UPLOADS_DIR = "uploads"

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

    try:
        if not os.path.exists(UPLOADS_DIR):
            print(f"Creating directory: {UPLOADS_DIR}")
            os.makedirs(UPLOADS_DIR)
            print(f"Directory '{UPLOADS_DIR}' created successfully.")
        else:
            print(f"Directory '{UPLOADS_DIR}' already exists.")
    except Exception as e:
        print(f"Error creating directory '{UPLOADS_DIR}': {e}")
        sys.exit(1)

    print("--- Application Initialization Complete ---")

if __name__ == "__main__":
    initialize_app()
# Public Speaking Coach MVP - Development Plan

This document outlines the development plan for the Public Speaking Coach MVP.

## Phase 1: Foundation

**Goal:** Establish the basic FastAPI application structure, serving a simple homepage with the correct styling. This phase focuses on getting the project running locally and ready for deployment.

**Tasks:**
1.  **Project Structure:**
    *   Create `app` directory.
    *   Create `app/main.py`: The core FastAPI application file.
    *   Create `app/templates` directory for Jinja2 templates.
    *   Create `app/static/css` directory for stylesheets.
2.  **FastAPI App:**
    *   In `app/main.py`, create a basic FastAPI instance.
    *   Implement the `/health` endpoint, which returns `{"status": "healthy"}`.
    *   Implement a root endpoint `/` that renders an `index.html` template.
3.  **Frontend:**
    *   Create `app/templates/base.html`: A base template for all pages.
    *   Create `app/templates/index.html`: The main landing page.
    *   Create `app/static/css/style.css`: Include the CSS variables from the design system.
4.  **Configuration:**
    *   Create a `requirements.txt` file with `fastapi`, `uvicorn`, `jinja2`, and `python-decouple`.
    *   Create a `.env` file for local environment variables (`DEBUG=True`, `DATABASE_URL=sqlite:///./app.db`).
    *   Create `railway.json` with the specified deployment configuration.

**Testing Checkpoint 1:**
*   Run `uvicorn app.main:app --reload` locally.
*   Access `http://localhost:8000/` and see the styled homepage.
*   Access `http://localhost:8000/health` and see `{"status": "healthy"}`.
*   Deploy to Railway and verify the health check.

## Phase 2: Database & Navigation

**Goal:** Set up the SQLite database and create the navigation structure for the different analysis views.

**Tasks:**
1.  **Database Setup:**
    *   Create `app/database.py` to manage the SQLite connection and table creation.
    *   Define the `videos`, `notes`, and `prompts` table schemas.
    *   Create a function to initialize the database.
2.  **Navigation:**
    *   In `app/main.py`, add routes for `/upload`, `/video/{video_id}`, `/audio/{video_id}`, `/text/{video_id}`, and `/report/{video_id}`.
    *   Create basic placeholder templates for each of these pages.
3.  **Database Testing:**
    *   Add a `/test-db` endpoint to `app/main.py` that performs a simple create and read operation on the database to verify connectivity.

**Testing Checkpoint 2:**
*   Run the application.
*   Access `http://localhost:8000/test-db` to confirm the database is working.
*   Navigate to all the newly created page routes and ensure they render without errors.

## Phase 3: File Upload

**Goal:** Implement the local file upload functionality with validation.

**Tasks:**
1.  **Upload Interface:**
    *   On the `/upload` page, create a drag-and-drop file upload interface using HTML and Alpine.js.
2.  **Backend Logic:**
    *   In `app/main.py`, create an endpoint to handle the file upload.
    *   Implement validation for file size (max 50MB) and file type (MP4, MOV, AVI, WEBM).
    *   Save the uploaded file to a local `uploads` directory.
    *   Store the file's metadata (filename, size, etc.) in the `videos` table.
    *   Redirect the user to the analysis view upon successful upload.

**Testing Checkpoint 3:**
*   Attempt to upload files of various sizes and types to test the validation logic.
*   Verify that valid files are saved to the `uploads` directory and their metadata is stored in the database.
*   Ensure that invalid files are rejected with a proper error message.

## Phase 4: R2 Integration

**Goal:** Replace local file storage with Cloudflare R2.

**Tasks:**
1.  **R2 Connection:**
    *   Add `boto3` to `requirements.txt`.
    *   Create `app/r2.py` to handle the connection to Cloudflare R2.
    *   Add R2-related environment variables to the `.env` file.
2.  **Update Upload Logic:**
    *   Modify the file upload endpoint in `app/main.py` to upload files to R2 instead of saving them locally.
    *   Implement a graceful fallback to local storage if R2 is not configured.
3.  **R2 Testing:**
    *   Create a `/test-r2` endpoint to verify the connection to R2.

**Testing Checkpoint 4:**
*   Access `http://localhost:8000/test-r2` to confirm the R2 connection.
*   Test the file upload functionality to ensure files are being uploaded to R2.
*   Test the fallback to local storage.

## Phase 5: Analysis Views & Notes

**Goal:** Build the three analysis views and the notes system.

**Tasks:**
1.  **Analysis Views:**
    *   **Video View:** Create a muted video player and display body language prompts.
    *   **Audio View:** Create an audio player and display voice/tone prompts.
    *   **Text View:** Create a text area for manual transcript input and display content analysis prompts.
2.  **Prompts:**
    *   Seed the `prompts` table with the guided questions for each view.
3.  **Notes System:**
    *   Create API endpoints to save and retrieve notes for each prompt.
    *   Use JavaScript to auto-save notes as the user types.
4.  **Report Generation:**
    *   Create the `/report/{video_id}` page to display all the notes for a given video.
    *   Implement "Download as text" and "Copy to clipboard" functionality.

**Testing Checkpoint 5:**
*   Upload a video and navigate to all three analysis views.
*   Add notes for each prompt and verify they are saved correctly.
*   Check that the notes persist between sessions.
*   View the compiled report and test the download and copy features.
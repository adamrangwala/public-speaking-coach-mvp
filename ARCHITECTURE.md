# Public Speaking Coach - System Architecture Diagram

This diagram illustrates the technical architecture and data flow of the Public Speaking Coach application.

'''mermaid
graph TD,
    subgraph User
        A[Browser]
    end

    subgraph Backend on Railway
        B[FastAPI Server]
        C[SQLite Database]
    end

    subgraph Cloudflare
        D[R2 Storage Bucket]
    end

    style User fill:#d4f0ff,stroke:#333,stroke-width:2px
    style Backend on Railway fill:#e6ffc2,stroke:#333,stroke-width:2px
    style Cloudflare fill:#fff0b3,stroke:#333,stroke-width:2px

    A -- "1. Upload Video (POST /upload)" --> B
    B -- "2. Save video to R2" --> D
    D -- "3. Return object key" --> B
    B -- "4. Store metadata in DB" --> C
    C -- "5. Return video ID" --> B
    B -- "6. Redirect to /video/{id}" --> A

    A -- "7. Request /video/{id}" --> B
    B -- "8. Fetch video data from DB" --> C
    C -- "9. Return video metadata" --> B
    B -- "10. Generate Presigned URL for video" --> D
    D -- "11. Return Presigned URL" --> B
    B -- "12. Render HTML with Presigned URL" --> A
    A -- "13. Stream video from R2" --> D

    A -- "14. Auto-save Note (POST /api/notes)" --> B
    B -- "15. Save note to DB" --> C
    C -- "16. Return success" --> B
    B -- "17. Return success" --> A

    A -- "18. Auto-save Transcript (POST /api/transcript)" --> B
    B -- "19. Save transcript to DB" --> C
    C -- "20. Return success" --> B
    B -- "21. Return success" --> A
'''

### Diagram Legend

*   **User (Browser):** The client-side application running in the user's web browser. It interacts with the backend through HTTP requests.
*   **Backend on Railway:**
    *   **FastAPI Server:** The core of the application that handles all business logic, API requests, and HTML page rendering.
    *   **SQLite Database:** The database that stores all application data, including video metadata, user notes, and transcripts.
*   **Cloudflare R2:** The object storage service used to store the uploaded video files securely.

### Key Data Flows

1.  **Video Upload:**
    *   The user uploads a video from the browser.
    *   The FastAPI server receives the file, uploads it directly to a private R2 bucket, and then saves the video's metadata (including the R2 object key) to the SQLite database.
    *   The user is redirected to the video analysis page.

2.  **Video Playback (Secure Streaming):**
    *   When the user visits an analysis page, the FastAPI server retrieves the video's metadata from the database.
    *   It then requests a temporary, secure **presigned URL** from R2 for the specific video file.
    *   This presigned URL is embedded in the HTML sent to the browser, allowing the video player to securely stream the content directly from R2 without exposing the private bucket.

3.  **Auto-Saving Notes & Transcript:**
    *   As the user types in the note or transcript text areas, the Alpine.js frontend sends the content to dedicated API endpoints (`/api/notes`, `/api/transcript`).
    *   The FastAPI server receives this data and saves it to the SQLite database, providing a seamless auto-save experience.
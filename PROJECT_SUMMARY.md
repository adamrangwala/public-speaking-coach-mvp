# Public Speaking Coach V4 - Project Summary

## 1. Project Overview

This project aimed to refactor and enhance the Public Speaking Coach, a web application designed to help users improve their public speaking skills. The core functionality involves users uploading a video of themselves speaking and then guiding them through a multi-step analysis of their vocal delivery, physical presence, and content.

The project focused on fixing critical bugs, improving the user experience, and preparing the application for future V4 feature enhancements, all while adhering to a "less than 200 lines per file" rule for maintainability.

## 2. Architecture

The application follows a modern web architecture, balancing performance and simplicity.

*   **Backend:** A Python-based backend using the **FastAPI** framework, which provides a robust and high-performance API.
*   **Frontend:** A server-side rendered frontend using **Jinja2** templates, enhanced with the **Alpine.js** JavaScript framework for interactivity. This allows for a dynamic user experience without the complexity of a full single-page application.
*   **Database:** A **SQLite** database, configured with cascading deletes to ensure data integrity. This is simple to manage and suitable for the application's scale.
*   **Video Processing:** **FFmpeg** is used for all video and audio manipulation, including transcoding videos into HLS (HTTP Live Streaming) format for adaptive streaming.
*   **Transcription:** The **AssemblyAI API** is used for automatic speech-to-text transcription. The implementation was refactored to use a robust polling mechanism.
*   **Storage:** The application is designed to work with both a local filesystem (for development) and **Cloudflare R2** object storage (for production), with a clear abstraction layer (`r2.py`).

## 3. Key Features & Styling

### Features Implemented:

*   **Guided User Onboarding:** The landing page was redesigned with a two-column layout. It now features an embedded YouTube tutorial and a clear, 4-step guide to explain the app's workflow.
*   **Step-by-Step Analysis Flow:** A persistent sidebar acts as a progress indicator, guiding the user through the four analysis stages: Audio, Video, Transcription, and Report.
*   **On-Demand Transcription:** The transcription process is now initiated manually by the user via an "Auto-Transcribe Audio" button. This provides better control and a more predictable user experience.
*   **Robust Video Uploads:** The application supports various video formats (MP4, MOV, AVI, WEBM) and provides a drag-and-drop interface with a progress bar.
*   **HLS Video Streaming:** Uploaded videos are transcoded into HLS format, enabling adaptive bitrate streaming for a smoother playback experience.

### Styling:

*   **Modern & Clean UI:** The application's visual style was modernized with a professional blue color palette, improved typography, and increased spacing for better readability.
*   **Consistent Design Language:** The UI uses a consistent card-based design with subtle shadows to create a clean, organized, and uncluttered interface.

## 4. Challenges & Resolutions

We faced several significant challenges during the refactoring process, primarily related to the transcription feature.

*   **Initial Problem:** The auto-generated transcript was not appearing on the frontend, despite logs showing it was saved to the database.

*   **Troubleshooting Journey:**
    1.  **Webhook & Caching:** We initially suspected a browser caching issue with the API endpoint that fetched the transcript. We implemented cache-busting techniques, but the problem persisted.
    2.  **Environment-Specific Issues:** We determined that the webhook-based approach, where AssemblyAI calls back to our server, was unreliable in the Railway deployment environment. This led to the decision to switch to a more robust polling mechanism.
    3.  **Polling Implementation:** We refactored the transcription logic to have our backend poll AssemblyAI for the result. This removed the dependency on incoming webhooks.
    4.  **Application Crash:** The initial polling implementation introduced a circular import, causing the entire application to fail on startup. This was resolved by restructuring the imports in `app/main.py` to load the transcription function correctly.

*   **Key Fix:** The critical fix was moving from a passive, webhook-dependent architecture to an active, polling-based one for transcription. This made the process self-contained within our application and removed the reliance on external services successfully reaching our server, which was the root cause of the failure.

This summary should provide all the necessary context to continue with the V4 feature development in a new session.
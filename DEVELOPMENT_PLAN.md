# Public Speaking Coach App - V2 Development Plan

This document outlines the development plan for V2 of the Public Speaking Coach App. The plan is divided into three phases, with a focus on incremental development, local testing, and deployment to Railway.

---

## Phase 1: UI/UX Polish

**Goal:** Enhance the user experience with a more responsive and interactive interface.

**Testing:** All features will be tested locally before deploying to Railway.

| Step | Feature | Implementation Details | Testing |
| :--- | :--- | :--- | :--- |
| 1.1 | **Upload Progress Bar** | - Use Alpine.js to manage the state of the upload (progress, error, success).<br>- Use `XMLHttpRequest` to handle the file upload and listen for the `progress` event.<br>- Update a visual progress bar in `upload.html`. | - Upload a small file and verify the progress bar updates correctly.<br>- Upload a large file to see the progress over time.<br>- Test error handling for failed uploads. |
| 1.2 | **Relative Timestamps** | - Integrate `timeago.js` into the `base.html` template.<br>- Create a new Jinja2 filter or a small JavaScript function to format timestamps on the frontend.<br>- Apply the filter to the video list on the index page. | - Verify that timestamps are displayed as "5 minutes ago", "yesterday", etc.<br>- Check edge cases like "just now" and dates far in the past. |
| 1.3 | **Visual Feedback** | - Add CSS transitions for hover effects on buttons and links in `style.css`.<br>- Implement a "Saved!" animation for the notes section using Alpine.js and CSS.<br>- Add subtle animations to page loads. | - Hover over all interactive elements to ensure smooth transitions.<br>- Verify the "Saved!" animation appears and disappears correctly after typing in the notes. |
| 1.4 | **Better Empty States** | - Update the `index.html` to show a more engaging message when there are no videos.<br>- Include a clear call-to-action to upload the first video. | - Delete all videos from the database and check the empty state message on the dashboard. |

---

## Phase 2: User Authentication

**Goal:** Implement secure user registration and login to protect user privacy.

**Testing:** All authentication features will be tested locally before deploying to Railway.

| Step | Feature | Implementation Details | Testing |
| :--- | :--- | :--- | :--- |
| 2.1 | **Database Schema Update** | - Add a `users` table (`id`, `email`, `hashed_password`).<br>- Add a `user_id` foreign key to the `videos` table. | - Run a migration to update the database schema.<br>- Verify the new tables and columns are created correctly. |
| 2.2 | **Registration & Login** | - Create registration and login pages (`register.html`, `login.html`).<br>- Implement password hashing using `passlib` with `bcrypt`.<br>- Create endpoints for user registration and login. | - Register a new user and verify the password is hashed in the database.<br>- Log in with the new user and verify a session is created. |
| 2.3 | **Session Management** | - Use JWT for session management.<br>- Store the JWT in an HTTP-only cookie for security. | - Verify the JWT is created on login and stored in a cookie.<br>- Verify the JWT is sent with subsequent requests. |
| 2.4 | **User-Aware Endpoints** | - Create a dependency to get the current user from the JWT.<br>- Protect all video-related endpoints to ensure users can only access their own videos. | - Log in as one user and verify they can only see their own videos.<br>- Try to access another user's video and verify it's not possible. |

---

## Phase 3: Auto-Transcription

**Goal:** Integrate a speech-to-text service to automatically transcribe user videos.

**Testing:** All transcription features will be tested locally before deploying to Railway.

| Step | Feature | Implementation Details | Testing |
| :--- | :--- | :--- | :--- |
| 3.1 | **Speech-to-Text Integration** | - Choose and integrate a speech-to-text API (e.g., AssemblyAI, Deepgram, OpenAI Whisper).<br>- Add API keys to the environment variables. | - Upload a video and verify the transcription is requested from the API. |
| 3.2 | **Background Task Processing** | - Use FastAPI's `BackgroundTasks` to process the transcription in the background.<br>- Add a `transcript_status` column to the `videos` table. | - Upload a video and verify the transcription status is updated correctly. |
| 3.3 | **Webhook Endpoint** | - Create a webhook endpoint to receive the completed transcript from the speech-to-text service.<br>- Update the `videos` table with the transcript and set the status to "completed". | - Mock a webhook call to the endpoint and verify the transcript is saved correctly. |

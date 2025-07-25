# Public Speaking Coach V4 Refactoring Project

This document outlines the development plan for refactoring the Public Speaking Coach application to Version 4. The plan is divided into phases, starting with critical bug fixes, followed by performance and feature enhancements.

## Phase 1: Critical Bug Fixes

### Task 1: Fix `.mov` Audio Playback Issue

- **Goal:** Ensure audio from `.mov` files plays correctly after processing.
- **Steps:**
    1.  **Analyze FFmpeg command:** Review the existing transcoding command in `app/video_processing.py`.
    2.  **Inspect `.mov` codecs:** Use `ffprobe` to identify the audio codec in a sample `.mov` file.
    3.  **Modify FFmpeg command:** Update the command to explicitly re-encode audio to AAC (`-c:a aac`).
    4.  **Test:** Process a sample `.mov` file and verify that both video and audio play correctly in the browser.

### Task 2: Fix Transcription Display Issue

- **Goal:** Ensure that completed transcriptions are displayed on the `/text/{video_id}` page.
- **Steps:**
    1.  **Review backend route:** Examine the FastAPI route in `app/main.py` that serves the transcription page.
    2.  **Verify data retrieval:** Check the database query to ensure it correctly fetches the transcription text.
    3.  **Inspect frontend template:** Review `app/templates/text.html` to confirm the Jinja2 template is correctly rendering the transcription data.
    4.  **Check for frontend errors:** Use browser developer tools to look for any JavaScript errors preventing the display of the transcription.

## Phase 2: V4 Performance Optimizations

### Task 3: Standardize Video Uploads

- **Goal:** Convert all uploaded videos to a standard format (H.264/MP4, 720p, 30fps).
- **Steps:**
    1.  **Update processing logic:** Modify the video upload handling in `app/video_processing.py`.
    2.  **Implement standardization function:** Create a function to apply a standard set of FFmpeg transformations:
        - Convert to MP4 container.
        - Set video codec to H.264 (`-c:v libx264`).
        - Set audio codec to AAC (`-c:a aac`).
        - Resize to 720p (`-vf "scale=-1:720"`).
        - Set frame rate to 30fps (`-r 30`).
        - Apply aggressive compression (`-crf 28`).

### Task 4: Implement Adaptive Bitrate Streaming

- **Goal:** Generate multiple quality versions (240p, 480p, 720p) for HLS adaptive streaming.
- **Steps:**
    1.  **Update FFmpeg commands:** Extend the transcoding script to generate multiple renditions of the video.
    2.  **Create master playlist:** Generate a master `.m3u8` playlist that references the individual stream playlists.
    3.  **Configure player:** Ensure the frontend HLS player is configured to use the master playlist for adaptive streaming.

### Task 5: Optimize Video Processing Workflow

- **Goal:** Improve the efficiency of the video processing pipeline.
- **Steps:**
    1.  **Implement two-pass encoding:** Modify the FFmpeg command to use a two-pass approach for better rate control and compression.
    2.  **Strip metadata:** Add the `-map_metadata -1` flag to the FFmpeg command to remove non-essential metadata.
    3.  **Generate thumbnails:** Create a function to extract a thumbnail from the video during processing.

## Phase 3: Storage and API Optimization

### Task 6: Optimize Storage

- **Goal:** Reduce cloud storage costs.
- **Steps:**
    1.  **Configure R2 Lifecycle Policies:** Set up rules in the Cloudflare R2 dashboard to transition older content to cheaper storage tiers.
    2.  **Cleanup intermediate files:** Ensure that temporary files created during transcoding are deleted.

### Task 7: Optimize API Usage

- **Goal:** Make more efficient use of the AssemblyAI API.
- **Steps:**
    1.  **Implement caching:** Add a caching layer for transcription results to prevent redundant API calls for the same file.

Once you approve this plan, I will be ready to switch to "code" mode and begin the implementation.
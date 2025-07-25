# UI/UX Improvement Plan

This document outlines the plan to enhance the user interface (UI) and user experience (UX) of the Public Speaking Coach application. The goal is to create a more intuitive, modern, and guided experience for the user.

## Phase 1: Landing Page Redesign

The landing page (`index.html`) is the user's first interaction with the app. It needs to be clear, concise, and action-oriented.

### Task 1.1: Embed Instructional Video

-   **Goal:** Immediately educate the user on the app's purpose and workflow.
-   **Action:** Embed the provided YouTube Short (`https://www.youtube.com/shorts/mXPIJosPsVU`) directly onto the landing page. This will serve as the primary instruction method.
-   **Implementation:** Use the YouTube embed code to display the video prominently. The embed URL will be `https://www.youtube.com/embed/mXPIJosPsVU`.

### Task 1.2: Create a Clear Step-by-Step Guide

-   **Goal:** Reinforce the video's message with a simple, scannable text guide.
-   **Action:** Add a section next to or below the video with four clear steps:
    1.  **Upload Your Video:** A brief instruction to upload a 3-5 minute video of yourself speaking.
    2.  **Analyze Your Voice:** Review the audio-only version to focus on tone, pace, and filler words.
    3.  **Review Your Presence:** Watch the video-only version to analyze body language and expressions.
    4.  **Refine Your Content:** Use the auto-generated transcript to check for clarity and conciseness.

### Task 1.3: Redesign the Layout

-   **Goal:** Create a modern, clean, and focused layout.
-   **Action:**
    -   Implement a two-column layout. The left column will feature the instructional video and the step-by-step guide. The right column will contain the primary call-to-action: the file upload component.
    -   Make the file upload area large, clear, and inviting.
    -   The list of previously uploaded videos will be moved below this main section, presented in a clean, card-based layout.

## Phase 2: Improving Navigation and User Flow

Once a video is uploaded, the user should feel guided through the analysis process.

### Task 2.1: Implement a Progress Indicator

-   **Goal:** Give users a clear sense of where they are in the analysis process.
-   **Action:** Modify the sidebar (`sidebar.html`) or create a new header in `base.html` to display a visual progress bar or stepper.
-   **Steps:**
    1.  `Audio Analysis`
    2.  `Video Analysis`
    3.  `Text Analysis`
    4.  `Final Report`
-   **Implementation:** The current step will be highlighted. This provides context and a clear path forward.

### Task 2.2: Enhance Page Titles and Instructions

-   **Goal:** Ensure each analysis page is self-explanatory.
-   **Action:** Review and update the titles and introductory text on `audio.html`, `video.html`, and `text.html` to be more direct and action-oriented, guiding the user on what to focus on for that specific step.

### Task 2.3: Consistent "Next Step" Navigation

-   **Goal:** Make it obvious how to proceed to the next stage of analysis.
-   **Action:** Ensure that the "Previous" and "Next" buttons are consistently placed and clearly labeled on all analysis pages. The final page should have a clear "Finish & View Report" button.

## Phase 3: Modernize Visual Style

A clean, modern aesthetic improves usability and perceived value.

### Task 3.1: Refine CSS and Styling

-   **Goal:** Update the visual design to be more sleek and professional.
-   **Action:**
    -   Update `static/css/style.css` with a refined color palette (e.g., using blues, greys, and a single accent color for actions).
    -   Improve typography for better readability.
    -   Increase spacing and use modern card designs with subtle shadows to create a cleaner, less cluttered interface.

Once you approve this plan, I will be ready to switch to "code" mode and begin the implementation, starting with the landing page redesign.
import os
import shutil
from datetime import datetime, timezone
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Body, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from .database import get_db_connection, create_tables
from .r2 import is_r2_configured, upload_file_to_r2, download_file_from_r2, test_r2_connection, generate_presigned_url
from .seed_prompts import seed_prompts
from .video_processing import transcode_to_hls
from .transcription import is_transcription_configured, submit_for_transcription

# --- Constants ---
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
UPLOADS_DIR = "uploads"
HLS_PLAYLIST_DIR = "hls_playlists"

app = FastAPI()

# --- Static Files & Templates ---
# Ensure static directories exist before mounting
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(HLS_PLAYLIST_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount(f"/{UPLOADS_DIR}", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount(f"/{HLS_PLAYLIST_DIR}", StaticFiles(directory=HLS_PLAYLIST_DIR), name="hls")

templates = Jinja2Templates(directory="app/templates")

def nl2br(value: str) -> str:
    """Converts newlines in a string to HTML <br> tags."""
    if not isinstance(value, str):
        return value
    return Markup(value.replace('\n', '<br>\n'))

templates.env.filters['nl2br'] = nl2br

@app.on_event("startup")
def on_startup():
    create_tables()
    seed_prompts()

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = get_db_connection()
    videos_cursor = conn.execute("SELECT id, original_filename, created_at FROM videos ORDER BY created_at DESC")
    videos = videos_cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "videos": videos})

@app.get("/video/{video_id}", response_class=HTMLResponse)
async def video_page(request: Request, video_id: int):
    return await analysis_page_factory("video", request, video_id)

@app.get("/audio/{video_id}", response_class=HTMLResponse)
async def audio_page(request: Request, video_id: int):
    return await analysis_page_factory("audio", request, video_id)

@app.get("/text/{video_id}", response_class=HTMLResponse)
async def text_page(request: Request, video_id: int):
    return await analysis_page_factory("text", request, video_id)

@app.get("/report/{video_id}", response_class=HTMLResponse)
async def report_page(request: Request, video_id: int):
    conn = get_db_connection()
    notes_cursor = conn.execute("""
        SELECT p.question, n.content, p.view_type
        FROM notes n
        JOIN prompts p ON n.prompt_id = p.id
        WHERE n.video_id = ?
        ORDER BY
            CASE p.view_type
                WHEN 'audio' THEN 1
                WHEN 'video' THEN 2
                WHEN 'text' THEN 3
                ELSE 4
            END,
            p.order_index
    """, (video_id,))
    notes_data = notes_cursor.fetchall()
    conn.close()

    # Group notes by view_type in the desired order
    report_sections_data = {
        "audio": [],
        "video": [],
        "text": []
    }
    for note in notes_data:
        view_type = note['view_type']
        if view_type in report_sections_data:
            report_sections_data[view_type].append(dict(note))

    # Create a list of sections in the correct order, with correct titles
    report_sections = [
        {"title": "Audio Image", "notes": report_sections_data["audio"]},
        {"title": "Video Image", "notes": report_sections_data["video"]},
        {"title": "Audio Transcription", "notes": report_sections_data["text"]},
    ]

    # Filter out empty sections
    report_sections = [section for section in report_sections if section["notes"]]

    return templates.TemplateResponse("report.html", {"request": request, "video_id": video_id, "report_sections": report_sections})

# --- API Endpoints ---

@app.post("/upload")
async def handle_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large (max 50MB).")
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    
    temp_filename = f"temp_{os.urandom(8).hex()}{file_ext}"
    temp_path = os.path.join(UPLOADS_DIR, temp_filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    upload_url = None
    db_filename = temp_filename

    if is_r2_configured():
        try:
            upload_file_to_r2(temp_path, db_filename)
            upload_url = "R2"
            os.remove(temp_path) # Clean up immediately after successful R2 upload
        except Exception as e:
            os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"R2 upload failed: {e}")
    else:
        upload_url = f"/{UPLOADS_DIR}/{db_filename}"

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO videos (filename, original_filename, file_size, mime_type, upload_url) VALUES (?, ?, ?, ?, ?)",
            (db_filename, file.filename, file.size, file.content_type, upload_url)
        )
        conn.commit()
        video_id = cursor.lastrowid
    except Exception as e:
        if not is_r2_configured() and os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

    # Start transcoding in the background
    background_tasks.add_task(transcode_and_update_db, temp_filename, video_id, is_r2_configured())

    return RedirectResponse(url=f"/audio/{video_id}", status_code=303)

@app.post("/api/notes")
async def save_note(
    video_id: int = Body(...),
    prompt_id: int = Body(...),
    view_type: str = Body(...),
    content: str = Body(...)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO notes (video_id, prompt_id, view_type, content)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(video_id, prompt_id) DO UPDATE SET
            content = excluded.content,
            created_at = CURRENT_TIMESTAMP
        """, (video_id, prompt_id, view_type, content))
        conn.commit()
        return {"status": "success", "message": "Note saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/transcript")
async def save_transcript(
    video_id: int = Body(...),
    content: str = Body(...)
):
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE videos SET transcript = ? WHERE id = ?",
            (content, video_id)
        )
        conn.commit()
        return {"status": "success", "message": "Transcript saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

@app.post("/api/webhook/transcription")
async def transcription_webhook(request: Request):
    """Webhook endpoint to receive transcription results from AssemblyAI."""
    data = await request.json()
    transcript_id = data.get("transcript_id")
    status = data.get("status")
    text = data.get("text")
    video_id = data.get("video_id") # We will pass this in the webhook URL

    if not all([transcript_id, status, text, video_id]):
        raise HTTPException(status_code=400, detail="Missing required fields in webhook data.")

    if status == "completed":
        conn = get_db_connection()
        try:
            conn.execute("UPDATE videos SET transcript = ? WHERE id = ?", (text, video_id))
            conn.commit()
        finally:
            conn.close()
    
    return {"status": "success"}

@app.delete("/api/video/{video_id}")
async def delete_video(video_id: int):
    conn = get_db_connection()
    try:
        # First, get the video's filename to delete the file
        video_cursor = conn.execute("SELECT filename FROM videos WHERE id = ?", (video_id,))
        video_data = video_cursor.fetchone()
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")

        # Delete from R2 or local storage
        if is_r2_configured():
            from .r2 import delete_file_from_r2
            try:
                delete_file_from_r2(video_data["filename"])
            except Exception as e:
                # Log the error but proceed to delete DB record
                print(f"Could not delete file from R2: {e}")
        else:
            # Clean up the permanent video file and its HLS playlist
            permanent_path = os.path.join(UPLOADS_DIR, video_data["filename"])
            if os.path.exists(permanent_path):
                os.remove(permanent_path)
            hls_dir = os.path.join(HLS_PLAYLIST_DIR, str(video_id))
            if os.path.exists(hls_dir):
                shutil.rmtree(hls_dir)

        # Delete the video record. Associated notes are deleted by CASCADE.
        conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()

        return {"status": "success", "message": "Video and associated data deleted."}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database or file system error: {e}")
    finally:
        conn.close()

# --- Health & Test Routes ---

@app.get("/health")
def read_health():
    return {"status": "healthy"}

@app.get("/test-db")
def test_db_endpoint():
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "db ok"}
    except Exception as e:
        return {"status": "db error", "error": str(e)}

@app.get("/test-r2")
def test_r2_endpoint():
    return test_r2_connection()

@app.get("/video-file/{video_id}")
async def get_video_file(video_id: int):
    """
    Redirects to a presigned URL for the video file in R2.
    This provides a stable URL for the transcription service.
    """
    conn = get_db_connection()
    video_cursor = conn.execute("SELECT filename FROM videos WHERE id = ?", (video_id,))
    video_data = video_cursor.fetchone()
    conn.close()

    if not video_data or not is_r2_configured():
        raise HTTPException(status_code=404, detail="Video not found or R2 not configured.")

    presigned_url = generate_presigned_url(video_data["filename"])
    if not presigned_url:
        raise HTTPException(status_code=500, detail="Could not generate presigned URL.")

    return RedirectResponse(url=presigned_url)

# --- Helper Functions ---

def transcode_and_update_db(temp_filename: str, video_id: int, is_r2: bool):
    """
    Background task to process video:
    1. Renames temp file to a permanent one (if local).
    2. Updates DB with permanent file path.
    3. Transcodes to HLS.
    4. Triggers transcription.
    """
    temp_path = os.path.join(UPLOADS_DIR, temp_filename)
    permanent_filename = temp_filename # On R2, the filename is already permanent
    video_path = temp_path

    try:
        conn = get_db_connection()

        # If not using R2, create a permanent file path and update the DB
        if not is_r2:
            file_ext = os.path.splitext(temp_filename)[1]
            permanent_filename = f"video_{video_id}{file_ext}"
            permanent_path = os.path.join(UPLOADS_DIR, permanent_filename)
            os.rename(temp_path, permanent_path)
            video_path = permanent_path # Use the new path for transcoding

            upload_url = f"/{UPLOADS_DIR}/{permanent_filename}"
            conn.execute(
                "UPDATE videos SET filename = ?, upload_url = ? WHERE id = ?",
                (permanent_filename, upload_url, video_id)
            )
            conn.commit()

        # Transcode to HLS
        hls_url = transcode_to_hls(video_path, video_id)
        conn.execute("UPDATE videos SET hls_playlist_url = ? WHERE id = ?", (hls_url, video_id))
        conn.commit()
        conn.close()

        # Trigger Transcription
        if is_transcription_configured():
            BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
            video_url = f"{BASE_URL}/video-file/{video_id}" if is_r2 else f"{BASE_URL}/{UPLOADS_DIR}/{permanent_filename}"
            webhook_url = f"{BASE_URL}/api/webhook/transcription?video_id={video_id}"
            submit_for_transcription(video_url, webhook_url)

    except Exception as e:
        print(f"Error during background processing for video_id {video_id}: {e}")
    finally:
        # Clean up the original temp file if it wasn't renamed (i.e., on R2)
        if is_r2 and os.path.exists(temp_path):
            os.remove(temp_path)

async def analysis_page_factory(view_type: str, request: Request, video_id: int):
    """Factory to render video, audio, or text analysis pages."""
    conn = get_db_connection()
    
    video_cursor = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    video_data = video_cursor.fetchone()
    if not video_data:
        conn.close()
        raise HTTPException(status_code=404, detail="Video not found")

    video = dict(video_data)

    # Determine the correct URL to use based on the page and configuration
    if is_r2_configured():
        if view_type == 'video' and video.get("hls_playlist_url"):
            # For the video page, prioritize the HLS stream
            video["upload_url"] = video["hls_playlist_url"]
        elif video.get("filename"):
            # For audio/text pages on R2, always generate a presigned URL
            presigned_url = generate_presigned_url(video["filename"])
            if presigned_url:
                video["upload_url"] = presigned_url
    elif view_type == 'video' and video.get("hls_playlist_url"):
        # For local video playback, use the HLS stream
        video["upload_url"] = video["hls_playlist_url"]
    # If local and not HLS, the default local file URL in the DB is used
    
    prompts_cursor = conn.execute("""
        SELECT p.id, p.question, p.order_index, n.content
        FROM prompts p
        LEFT JOIN notes n ON p.id = n.prompt_id AND n.video_id = ?
        WHERE p.view_type = ?
        ORDER BY p.order_index
    """, (video_id, view_type))
    prompts = prompts_cursor.fetchall()
    
    conn.close()
    
    template_name = f"{view_type}.html"
    context = {
        "request": request,
        "video": video,
        "prompts": prompts,
        "video_id": video_id
    }
    return templates.TemplateResponse(template_name, context)
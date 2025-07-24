import os
import shutil
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from .database import get_db_connection, create_tables
from .r2 import is_r2_configured, upload_file_to_r2, test_r2_connection

# --- Constants ---
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
UPLOADS_DIR = "uploads"

app = FastAPI()

# --- Static Files & Templates ---
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

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
    # Fetch all notes for the video, joined with their prompts
    notes_cursor = conn.execute("""
        SELECT p.question, n.content
        FROM notes n
        JOIN prompts p ON n.prompt_id = p.id
        WHERE n.video_id = ?
        ORDER BY p.view_type, p.order_index
    """, (video_id,))
    notes = notes_cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("report.html", {"request": request, "video_id": video_id, "notes": notes})

# --- API Endpoints ---

@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    # (Code from previous phase, unchanged)
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
            upload_url = upload_file_to_r2(temp_path, temp_filename)
            os.remove(temp_path)
        except Exception as e:
            os.remove(temp_path)
            raise HTTPException(status_code=500, detail=f"R2 upload failed: {e}")
    else:
        upload_url = f"/{UPLOADS_DIR}/{temp_filename}"
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
    return RedirectResponse(url=f"/video/{video_id}", status_code=303)

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
        # Use INSERT OR REPLACE to handle both new notes and updates
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

# --- Health & Test Routes ---

@app.get("/health")
def read_health():
    return {"status": "healthy"}

@app.get("/test-db")
def test_db_endpoint():
    # (Code from previous phase, unchanged)
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

# --- Helper Functions ---

async def analysis_page_factory(view_type: str, request: Request, video_id: int):
    """Factory to render video, audio, or text analysis pages."""
    conn = get_db_connection()
    
    # Fetch video details
    video_cursor = conn.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
    video = video_cursor.fetchone()
    if not video:
        conn.close()
        raise HTTPException(status_code=404, detail="Video not found")

    # Fetch prompts and any existing notes for this view
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
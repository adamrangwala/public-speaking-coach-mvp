import os
import shutil
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .database import get_db_connection, create_tables

# --- Constants ---
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"}
UPLOADS_DIR = "uploads"

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def on_startup():
    create_tables()
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def read_health():
    return {"status": "healthy"}

@app.get("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        # Simple query to test connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "db ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    # 1. Validate File Size
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large (max 50MB).")

    # 2. Validate File Type (Extension and MIME)
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload MP4, MOV, AVI, or WEBM.")

    # 3. Save File Locally
    safe_filename = f"upload_{os.urandom(8).hex()}{file_ext}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        file.file.close()

    # 4. Store Metadata in Database
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO videos (filename, original_filename, file_size) VALUES (?, ?, ?)",
            (safe_filename, file.filename, file.size)
        )
        conn.commit()
        video_id = cursor.lastrowid
    except Exception as e:
        # Clean up saved file if DB insert fails
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error on insert: {e}")
    finally:
        conn.close()

    # 5. Redirect to Video Analysis Page
    return RedirectResponse(url=f"/video/{video_id}", status_code=303)


@app.get("/video/{video_id}", response_class=HTMLResponse)
async def video_page(request: Request, video_id: int):
    return templates.TemplateResponse("video.html", {"request": request, "video_id": video_id})

@app.get("/audio/{video_id}", response_class=HTMLResponse)
async def audio_page(request: Request, video_id: int):
    return templates.TemplateResponse("audio.html", {"request": request, "video_id": video_id})

@app.get("/text/{video_id}", response_class=HTMLResponse)
async def text_page(request: Request, video_id: int):
    return templates.TemplateResponse("text.html", {"request": request, "video_id": video_id})

@app.get("/report/{video_id}", response_class=HTMLResponse)
async def report_page(request: Request, video_id: int):
    return templates.TemplateResponse("report.html", {"request": request, "video_id": video_id})
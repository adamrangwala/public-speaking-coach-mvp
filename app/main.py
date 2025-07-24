from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
def health_check():
    """
    Health check endpoint for deployment verification.
    """
    return {"status": "healthy"}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index page.
    """
    return templates.TemplateResponse("index.html", {"request": request})
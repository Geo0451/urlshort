import string
import random
import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Bare-Minimum URL Shortener")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
DATABASE = "urls.db"

def init_db():
    """Create the database table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            long_url TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Pydantic model to validate incoming data from the user
class URLRequest(BaseModel):
    long_url: str

def generate_short_id(length: int = 6) -> str:
    """Generates a random 6-character string (e.g., 'aB3xZ9')"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

# Serve static files first (before dynamic routes)
@app.get("/")
async def root():
    """Serve index.html"""
    return FileResponse("index.html", media_type="text/html")

@app.get("/style.css")
async def serve_css():
    """Serve CSS file"""
    return FileResponse("style.css", media_type="text/css")

@app.get("/script.js")
async def serve_js():
    """Serve JavaScript file"""
    return FileResponse("script.js", media_type="application/javascript")

@app.post("/shorten")
def shorten_url(request: URLRequest):
    """Endpoint 1: Takes a long URL, creates a short ID, saves it, and returns it."""
    long_url = request.long_url
    
    # Check if this URL is already shortened to avoid duplicates
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT short_id FROM urls WHERE long_url = ?", (long_url,))
    result = cursor.fetchone()
    
    if result:
        conn.close()
        return {"short_url": f"http://127.0.0.1:8000/{result[0]}"}
    
    # Generate a unique short ID
    short_id = generate_short_id()
    while True:
        cursor.execute("SELECT 1 FROM urls WHERE short_id = ?", (short_id,))
        if not cursor.fetchone():
            break
        short_id = generate_short_id()
    
    # Save to database
    cursor.execute("INSERT INTO urls (short_id, long_url) VALUES (?, ?)", (short_id, long_url))
    conn.commit()
    conn.close()
    
    return {"short_url": f"http://127.0.0.1:8000/{short_id}"}

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    """Endpoint 2: Looks up the short ID and automatically redirects the browser."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT long_url FROM urls WHERE short_id = ?", (short_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    original_url = result[0]
    
    # Ensure URL has a protocol so the browser doesn't treat it as a local path
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url
        
    return RedirectResponse(
        url=original_url, 
        status_code=301,
        headers={"Cache-Control": "public, max-age=31536000"}
    )

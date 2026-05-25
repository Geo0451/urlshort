import string
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Bare-Minimum URL Shortener")

# Our in-memory database (a simple Python dictionary)
# Format: {"short_id": "original_long_url"}
db = {}

# Pydantic model to validate incoming data from the user
class URLRequest(BaseModel):
    long_url: str

def generate_short_id(length: int = 6) -> str:
    """Generates a random 6-character string (e.g., 'aB3xZ9')"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

@app.post("/shorten")
def shorten_url(request: URLRequest):
    """Endpoint 1: Takes a long URL, creates a short ID, saves it, and returns it."""
    long_url = request.long_url
    
    # Check if this URL is already shortened to avoid duplicate keys
    for short_id, original_url in db.items():
        if original_url == long_url:
            return {"short_url": f"http://127.0.0.1:8000/{short_id}"}
            
    # Generate a unique short ID
    short_id = generate_short_id()
    while short_id in db:
        short_id = generate_short_id()
        
    # Save to our dictionary
    db[short_id] = long_url
    
    return {"short_url": f"http://127.0.0.1:8000/{short_id}"}

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    """Endpoint 2: Looks up the short ID and automatically redirects the browser."""
    if short_id not in db:
        raise HTTPException(status_code=404, detail="Short URL not found")
        
    original_url = db[short_id]
    
    # Ensure URL has a protocol so the browser doesn't treat it as a local path
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url
        
    return RedirectResponse(url=original_url)

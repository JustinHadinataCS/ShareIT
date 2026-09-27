from pathlib import Path

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.rate_limit import limiter, rate_limit_exceeded
from app.routers import files, shares
from app.spa import SPAStaticFiles

# The Docker image copies the built React app here. Locally it doesn't exist and Vite serves the frontend.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="ShareIT")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded)
app.include_router(files.router)
app.include_router(shares.router)

# Mounted last so the API routes above always match first.
if STATIC_DIR.is_dir():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="frontend")

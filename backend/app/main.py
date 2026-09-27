from pathlib import Path

from fastapi import FastAPI

from app.routers import files
from app.spa import SPAStaticFiles

# The Docker image copies the built React app here. Locally it doesn't exist and Vite serves the frontend.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="ShareIT")
app.include_router(files.router)

# Mounted last so the API routes above always match first.
if STATIC_DIR.is_dir():
    app.mount("/", SPAStaticFiles(directory=STATIC_DIR, html=True), name="frontend")

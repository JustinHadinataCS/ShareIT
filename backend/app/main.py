from fastapi import FastAPI

from app.routers import files

app = FastAPI(title="ShareIT")
app.include_router(files.router)

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import admin, photos, results, upload, voting, ws

app = FastAPI(title="Photo Contest")

origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(photos.router)
app.include_router(voting.router)
app.include_router(results.router)
app.include_router(admin.router)
app.include_router(ws.router)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if not os.path.isdir(STATIC_DIR):
        raise HTTPException(status_code=404)
    candidate = os.path.join(STATIC_DIR, full_path) if full_path else None
    if candidate and os.path.isfile(candidate):
        return FileResponse(candidate)
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

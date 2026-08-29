import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
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


@app.on_event("startup")
async def startup():
    os.makedirs(settings.photos_dir, exist_ok=True)

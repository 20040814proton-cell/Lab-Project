import os
from typing import List
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import init_db, ping_db
from routers import students, upload, posts, life, showcase, auth, register, users, activities, projects, software, invites, admin, forum

app = FastAPI()

def parse_csv_env(name: str, default: List[str]):
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    return [item.strip().rstrip("/") for item in raw.split(",") if item.strip()]

default_origins = [
    "http://localhost:3333",
    "http://127.0.0.1:3333",
]
origins = parse_csv_env("LAB_CORS_ORIGINS", default_origins)
allow_origin_regex = os.getenv("LAB_CORS_ORIGIN_REGEX")
if not allow_origin_regex and origins == default_origins:
    allow_origin_regex = r"^http://(localhost|127\.0\.0\.1):\d+$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_db():
    await init_db()

STATIC_DIR = os.getenv("LAB_STATIC_DIR", "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(register.router, prefix="/api", tags=["register"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(life.router, prefix="/api/life", tags=["life"])
app.include_router(activities.router, prefix="/api/activities", tags=["activities"])
app.include_router(showcase.router, prefix="/api/showcase", tags=["showcase"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(software.router, prefix="/api/software", tags=["software"])
app.include_router(invites.router, prefix="/api/invites", tags=["invites"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(forum.router, prefix="/api/forum", tags=["forum"])

@app.get("/")
async def read_root():
    return {"status": "Lab Backend Running"}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    if await ping_db():
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Database not ready")

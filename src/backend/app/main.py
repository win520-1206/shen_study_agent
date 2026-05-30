from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routers.students import router
from .routers.stream import router as stream_router
from .services.bootstrap import init_db

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


init_db()

app = FastAPI(
    title="LearnMate-AI API",
    description="MVP backend for the China Software Cup A3 personalized learning multi-agent system.",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(stream_router)

# Serve frontend static files
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")


@app.get("/")
def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"project": "LearnMate-AI", "status": "running", "message": "Frontend not built. Run: cd src/frontend && npm run build"}


@app.get("/api")
def api_info():
    return {
        "project": "LearnMate-AI",
        "status": "running",
        "message": "Use /docs for the API explorer.",
    }

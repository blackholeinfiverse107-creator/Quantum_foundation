import sys
import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# -------------------------------------------------
# Path setup
# -------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

# -------------------------------------------------
# Optional Sentry
# -------------------------------------------------
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,
        environment=os.getenv("ENV", "production"),
    )

# -------------------------------------------------
# Local imports
# -------------------------------------------------
from app.core.logging import setup_logging, get_logger
from app.core.database import create_tables
from app.core.security import rate_limit, audit_log
from app.api.assistant import router as assistant_router
from app.routers.intent import router as intent_router
from app.routers.summarize import router as summarize_router
from app.routers.task import router as task_router
from app.routers.respond import router as respond_router
from app.routers.rl_action import router as rl_action_router
from app.routers.embed import router as embed_router
from app.routers.voice_stt import router as voice_stt_router
from app.routers.voice_tts import router as voice_tts_router
from app.routers.external_llm import router as external_llm_router
from app.routers.external_app import router as external_app_router
from app.routers.decision_hub import router as decision_hub_router

# -------------------------------------------------
# Logging
# -------------------------------------------------
setup_logging()
logger = get_logger(__name__)

# -------------------------------------------------
# App lifespan
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(
    title="AI Assistant Backend",
    description="Production-locked Assistant Backend",
    version="3.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# Security Middleware
# -------------------------------------------------
@app.middleware("http")
async def security_middleware(request: Request, call_next):

    # Allow health check without auth
    if request.url.path in ["/health"]:
        return await call_next(request)

    if request.url.path.startswith("/api"):
        rate_limit(request)

        api_key = request.headers.get("X-API-Key")
        if api_key != os.getenv("API_KEY"):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed"}
            )

        audit_log(request, "api_key_user")

    return await call_next(request)

# -------------------------------------------------
# ONLY PUBLIC ROUTER (LOCKED)
# -------------------------------------------------
app.include_router(assistant_router)
# Internal routers (secured via API key middleware)
app.include_router(intent_router, prefix="/api")
app.include_router(summarize_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(respond_router, prefix="/api")
app.include_router(rl_action_router, prefix="/api")
app.include_router(embed_router, prefix="/api")
app.include_router(voice_stt_router, prefix="/api")
app.include_router(voice_tts_router, prefix="/api")
app.include_router(external_llm_router, prefix="/api")
app.include_router(external_app_router, prefix="/api")
app.include_router(decision_hub_router, prefix="/api")

# -------------------------------------------------
# System Endpoints
# -------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/")
async def root():
    return {"message": "Assistant Core v3 API"}

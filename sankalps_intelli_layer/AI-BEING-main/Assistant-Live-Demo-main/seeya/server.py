from typing import Any, Dict, List, Optional, Literal
from fastapi import FastAPI, Query, Header, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid
import os
import asyncio

from .summaryflow_v4 import summarize_message
from .summaryflow_v3 import _preprocess_text
from .context_cleaner_v4 import clean_all
from .context_loader import ContextLoader


Platform = Literal["whatsapp", "email", "instagram", "sms"]
Device = Literal["ios", "android", "web", "windows", "macos", "unknown"]
Intent = Literal["meeting", "reminder", "question", "task", "note"]
Urgency = Literal["low", "medium", "high"]


class SummarizeInput(BaseModel):
    user_id: str
    platform: Platform
    message_id: str
    message_text: str
    timestamp: str


class DecisionHubSummary(BaseModel):
    summary_id: str
    user_id: str
    platform: Platform
    message_id: str
    summary: str
    intent: Intent
    urgency: Urgency
    entities: Dict[str, Any]
    context_flags: List[str]
    generated_at: str
    device_context: Device


class CleanInput(BaseModel):
    platform: Platform
    message_text: str


class CleanOutput(BaseModel):
    cleaned_text: str


class TaskObject(BaseModel):
    task_id: str
    user_id: Optional[str]
    summary_id: Optional[str]
    task_summary: str
    task_type: str
    external_target: str
    priority: str
    scheduled_for: Optional[str]
    status: str
    platform: Optional[str]
    device_context: Optional[str]
    created_at: str


class ContextFlowResponse(BaseModel):
    status: str
    timestamp: str
    trace_id: str
    data: TaskObject


app = FastAPI()
loader = ContextLoader()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8501").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def api_health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}

_scheduler_task = None

async def _periodic_ingest():
    interval = int(os.environ.get("CONTEXTFLOW_INGEST_INTERVAL_SECONDS", "300"))
    while True:
        try:
            stats = loader.get_statistics()
            # Simple heartbeat log; extend to ingest pipelines if needed
            print(f"[ContextFlow Scheduler] Stats: total_messages={stats.get('total_messages', 0)} at {datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}")
            try:
                from .priority_model import Prioritizer
                p = Prioritizer()
                p.update_from_feedback_table()
                p.decay_exploration()
                lr_stats = p.get_learning_stats()
                print(f"[ContextFlow Scheduler] RL learning updated: total_states={lr_stats.get('total_states')}, avg_reward={lr_stats.get('avg_reward')}")
            except Exception as e:
                print(f"[ContextFlow Scheduler] RL update error: {e}")
        except Exception as e:
            print(f"[ContextFlow Scheduler] Error: {e}")
        await asyncio.sleep(interval)

@app.on_event("startup")
async def _on_startup():
    global _scheduler_task
    enable = os.environ.get("ENABLE_CONTEXTFLOW_SCHEDULER", "true").lower() == "true"
    if enable:
        _scheduler_task = asyncio.create_task(_periodic_ingest())

@app.on_event("shutdown")
async def _on_shutdown():
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        _scheduler_task = None

def _require_api_key(x_api_key: Optional[str] = Header(default=None)):
    expected = os.environ.get("CONTEXTFLOW_API_KEY")
    if expected:
        if not x_api_key or x_api_key != expected:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.post("/api/summarize", response_model=DecisionHubSummary)
def api_summarize(payload: SummarizeInput):
    result = summarize_message(payload.dict())
    return DecisionHubSummary(**result)

@app.post("/api/summarize_and_task", response_model=ContextFlowResponse)
def api_summarize_and_task(payload: SummarizeInput, _auth=Depends(_require_api_key)):
    from .contextflow_v4 import normalize_task, save_task_to_db
    summary = summarize_message(payload.dict())
    task = normalize_task(summary)
    trace_id = str(uuid.uuid4())
    try:
        save_task_to_db(task)
    except Exception as e:
        print(f"Error saving to DB: {e}")
    return ContextFlowResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        trace_id=trace_id,
        data=TaskObject(**task)
    )


@app.get("/api/context")
def api_context(
    user_id: str = Query(...),
    platform: Platform = Query(...),
    limit: int = Query(3, ge=1, le=50),
):
    return loader.get_context(user_id, platform, limit)


@app.post("/api/message_cleaner", response_model=CleanOutput)
def api_message_cleaner(payload: CleanInput):
    base_clean, _ = clean_all(payload.platform, payload.message_text)
    if payload.platform == "email":
        cleaned = base_clean
    else:
        cleaned = _preprocess_text(payload.platform, base_clean)
    return CleanOutput(cleaned_text=cleaned)


@app.post("/api/taskify", response_model=TaskObject)
def api_taskify(payload: DecisionHubSummary):
    from .contextflow_v4 import normalize_task, save_task_to_db
    task = normalize_task(payload.dict())
    try:
        save_task_to_db(task)
    except Exception as e:
        print(f"Error saving to DB: {e}")
    return TaskObject(**task)


@app.post("/api/contextflow_task", response_model=ContextFlowResponse)
def api_contextflow_task(payload: DecisionHubSummary, _auth=Depends(_require_api_key)):
    from .contextflow_v4 import normalize_task, save_task_to_db
    
    trace_id = str(uuid.uuid4())
    task = normalize_task(payload.dict())
    
    try:
        save_task_to_db(task)
    except Exception as e:
        print(f"Error saving to DB: {e}")
        
    return ContextFlowResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        trace_id=trace_id,
        data=TaskObject(**task)
    )


@app.get("/api/tasks", response_model=List[TaskObject])
def api_get_tasks(user_id: str = Query(...), pending_only: bool = False, _auth=Depends(_require_api_key)):
    from .task_db_v4 import get_tasks_for_user, get_pending_tasks
    
    if pending_only:
        # Note: get_pending_tasks in task_db_v4 currently returns ALL pending tasks, 
        # but for API security we should probably filter by user_id if possible.
        # For now, let's filter in python if the helper doesn't support it.
        tasks = get_pending_tasks()
        return [TaskObject(**t) for t in tasks if t.get('user_id') == user_id]
    else:
        tasks = get_tasks_for_user(user_id)
        return [TaskObject(**t) for t in tasks]

@app.get("/api/task_trends")
def api_task_trends(user_id: Optional[str] = None, _auth=Depends(_require_api_key)):
    from .task_db_v4 import get_task_trends
    return get_task_trends(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", "8000")))

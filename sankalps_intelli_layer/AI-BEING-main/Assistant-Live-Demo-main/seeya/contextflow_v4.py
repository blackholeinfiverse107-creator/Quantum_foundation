import json
import uuid
import sys
import os
from datetime import datetime, timezone
import dateparser
from dateparser.search import search_dates

# Add parent directory to path to import nilesh
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try importing, handle if nilesh module structure is different or path is tricky
try:
    from nilesh.utils.db import get_db
    from nilesh.utils.schema import ensure_schema
except ImportError:
    # Fallback if running from a different context
    print("Warning: Could not import nilesh utils. DB operations might fail.")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nilesh', 'data', 'assistant_core.db'))

def generate_task_id():
    return f"t_{uuid.uuid4().hex[:8]}"

EXTERNAL_TARGET_KEYWORDS = {
    "calendar": ["meeting", "call", "zoom"],
    "crm": ["invoice", "payment", "client"],
    "todo_remind": ["remind", "remember", "follow up", "followup"],
}

INTENT_NORMALIZATION = {
    "confirm_meeting": "meeting",
    "schedule_meeting": "meeting",
    "meeting": "meeting",
    "reminder": "reminder",
    "follow_up": "follow-up",
    "followup": "follow-up",
    "task": "task",
    "note": "note",
}

def normalize_task_type(intent_str: str, summary_str: str) -> str:
    i = (intent_str or "").lower()
    t = INTENT_NORMALIZATION.get(i)
    if t:
        return t
    s = (summary_str or "").lower()
    if ("meeting" in i) or ("schedule" in i) or ("meeting" in s) or ("call" in s):
        return "meeting"
    if "reminder" in i or "remind" in s:
        return "reminder"
    if "follow_up" in i or "followup" in i or "follow up" in s:
        return "follow-up"
    return "note"

def map_external_target(intent_str: str, summary_str: str, scheduled_for: str | None) -> str:
    i = (intent_str or "").lower()
    s = (summary_str or "").lower()
    # Mapping rules:
    # - meeting/call/zoom -> calendar
    # - invoice/payment/client -> crm
    # - remind/remember/follow up AND no clear date -> todo
    # - else -> none
    for kw in EXTERNAL_TARGET_KEYWORDS["calendar"]:
        if kw in i or kw in s:
            return "calendar"
    for kw in EXTERNAL_TARGET_KEYWORDS["crm"]:
        if kw in i or kw in s:
            return "crm"
    if scheduled_for is None:
        for kw in EXTERNAL_TARGET_KEYWORDS["todo_remind"]:
            if (kw in i or kw in s):
                return "todo"
    return "none"
def _parse_schedule_from_text(text: str, anchor_iso: str | None) -> str | None:
    if not text:
        return None
    try:
        if anchor_iso and isinstance(anchor_iso, str):
            base = datetime.fromisoformat(anchor_iso.replace("Z", "+00:00")).astimezone(timezone.utc)
        else:
            base = datetime.now(timezone.utc)
        res = search_dates(
            text,
            settings={
                "RELATIVE_BASE": base.replace(tzinfo=None),
                "PREFER_DATES_FROM": "future",
            },
        )
        if not res or len(res) == 0:
            return None
        dt = res[0][1]
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        return None
def _format_ampm(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(timezone.utc)
        hour = dt.hour % 12 or 12
        minute = dt.minute
        ampm = "AM" if dt.hour < 12 else "PM"
        if minute == 0:
            return f"{hour} {ampm}"
        return f"{hour}:{minute:02d} {ampm}"
    except Exception:
        return None

def normalize_task(summary_data):
    """
    Takes a summary JSON (from Seeya) and returns a normalized task object.
    """
    # Extract fields
    summary_id = summary_data.get("summary_id")
    user_id = summary_data.get("user_id")
    platform = summary_data.get("platform")
    summary_text = summary_data.get("summary")
    intent = summary_data.get("intent", "").lower()
    urgency = summary_data.get("urgency", "low").lower()
    entities = summary_data.get("entities", {})
    device_context = summary_data.get("device_context")
    
    task_type = normalize_task_type(intent, summary_text)
    
    scheduled_for = entities.get("datetime") or _parse_schedule_from_text(summary_text, summary_data.get("generated_at"))
    people = entities.get("person") or []
    first_person = (people[0] if isinstance(people, list) and people else None)
    time_str = _format_ampm(scheduled_for) if scheduled_for else None
    external_target = map_external_target(intent, summary_text, scheduled_for)
    
    priority = derive_priority(urgency, task_type, scheduled_for, summary_text)
    if task_type == "meeting" and first_person and time_str:
        task_summary = f"Confirm {time_str} meeting with {first_person}."
    elif task_type == "follow-up" and first_person:
        task_summary = f"Follow up with {first_person}."
    elif task_type == "reminder" and first_person:
        task_summary = f"Reminder related to {first_person}."
    else:
        task_summary = summary_text
    
    # Create Task Object
    task_object = {
        "task_id": generate_task_id(),
        "user_id": user_id,
        "summary_id": summary_id,
        "task_summary": task_summary,
        "task_type": task_type,
        "external_target": external_target,
        "priority": priority,
        "scheduled_for": scheduled_for,
        "status": "pending",
        "platform": platform,
        "device_context": device_context,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    
    return task_object

from .task_db_v4 import save_task

def derive_priority(u: str, tt: str, sched: str | None, text: str) -> str:
    uu = (u or "low").lower()
    base = uu if uu in ["low", "medium", "high"] else "low"
    txt = (text or "").lower()
    if "urgent" in txt or "asap" in txt:
        return "high"
    if tt == "meeting" and sched:
        try:
            now = datetime.now(timezone.utc)
            dt = datetime.fromisoformat(sched.replace("Z", "+00:00")).astimezone(timezone.utc)
            if (dt - now).total_seconds() <= 24 * 3600:
                return "high"
        except Exception:
            pass
    return base

def save_task_to_db(task_object):
    """
    Writes the task object to Nilesh's unified DB via task_db_v4 helper.
    """
    print(f"Delegating DB save for task {task_object['task_id']} to task_db_v4...")
    save_task(task_object)
    print(f"Task {task_object['task_id']} saved to DB.")

def main():
    # Sample Input
    sample_input = {
        "summary_id": "s_123",
        "user_id": "abc123",
        "platform": "whatsapp",
        "message_id": "m123",
        "summary": "User wants to confirm a 5 PM meeting with Priya tomorrow.",
        "intent": "confirm_meeting",
        "urgency": "medium",
        "entities": {
            "person": ["Priya"],
            "datetime": "2025-11-21T17:00:00Z"
        },
        "context_flags": ["has_date", "has_person", "follow_up"],
        "device_context": "ios",
        "generated_at": "2025-11-20T14:00:02Z"
    }
    
    # Process
    print("Normalizing task...")
    task = normalize_task(sample_input)
    print("Generated Task Object:")
    print(json.dumps(task, indent=2))
    
    # Save to DB
    print("Saving to DB...")
    save_task_to_db(task)

if __name__ == "__main__":
    main()

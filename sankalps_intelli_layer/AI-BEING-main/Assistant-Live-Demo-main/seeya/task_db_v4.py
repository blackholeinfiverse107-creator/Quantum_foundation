import os
import sys
from datetime import datetime, timezone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from nilesh.utils.db import get_db
from nilesh.utils.schema import ensure_schema

def _get_db_path():
    env_path = os.environ.get("ASSISTANT_CORE_DB_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    try:
        module_db = globals().get("DB_PATH")
        if module_db and os.path.exists(module_db):
            return module_db
    except Exception:
        pass
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nilesh', 'data', 'assistant_core.db'))

def _utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def save_task(task_dict: dict):
    db_path = _get_db_path()
    ensure_schema(db_path)
    created_at = task_dict.get("created_at") or _utc_now()
    with get_db(db_path) as conn:
        conn.execute(
            """
            INSERT INTO tasks (
                trace_id, task_id, user_id, summary_id, task_summary,
                task_type, external_target, priority, scheduled_for,
                status, platform, device_context, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_dict["task_id"],
                task_dict["task_id"],
                task_dict.get("user_id"),
                task_dict.get("summary_id"),
                task_dict.get("task_summary"),
                task_dict.get("task_type"),
                task_dict.get("external_target"),
                task_dict.get("priority"),
                task_dict.get("scheduled_for"),
                task_dict.get("status", "pending"),
                task_dict.get("platform"),
                task_dict.get("device_context"),
                created_at,
            ),
        )
        conn.commit()

def get_tasks_for_user(user_id: str) -> list[dict]:
    db_path = _get_db_path()
    ensure_schema(db_path)
    with get_db(db_path) as conn:
        cur = conn.execute(
            """
            SELECT task_id, user_id, summary_id, task_summary, task_type,
                   external_target, priority, scheduled_for, status,
                   platform, device_context, created_at
            FROM tasks
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def get_pending_tasks() -> list[dict]:
    db_path = _get_db_path()
    ensure_schema(db_path)
    with get_db(db_path) as conn:
        cur = conn.execute(
            """
            SELECT task_id, user_id, summary_id, task_summary, task_type,
                   external_target, priority, scheduled_for, status,
                   platform, device_context, created_at
            FROM tasks
            WHERE status = 'pending'
            ORDER BY id DESC
            """
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def get_task_trends(user_id: str | None = None) -> dict:
    db_path = _get_db_path()
    ensure_schema(db_path)
    with get_db(db_path) as conn:
        where = ""
        params = ()
        if user_id:
            where = "WHERE user_id = ?"
            params = (user_id,)
        cur = conn.execute(
            f"""
            SELECT DATE(created_at) AS d, COUNT(*) AS c
            FROM tasks
            {where}
            GROUP BY DATE(created_at)
            ORDER BY d
            """,
            params,
        )
        daily = [{"date": r["d"], "count": r["c"]} for r in cur.fetchall()]
        cur = conn.execute(
            f"""
            SELECT external_target AS t, COUNT(*) AS c
            FROM tasks
            {where}
            GROUP BY external_target
            """,
            params,
        )
        targets = {r["t"] or "none": r["c"] for r in cur.fetchall()}
        cur = conn.execute(
            f"""
            SELECT priority AS p, COUNT(*) AS c
            FROM tasks
            {where}
            GROUP BY priority
            """,
            params,
        )
        priorities = {r["p"] or "low": r["c"] for r in cur.fetchall()}
    return {"daily": daily, "targets": targets, "priorities": priorities}

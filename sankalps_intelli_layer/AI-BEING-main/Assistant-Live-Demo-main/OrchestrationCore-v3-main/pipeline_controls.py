import time
import sqlite3
import datetime
from connectors.calendar_connector import send as calendar_send
from connectors.email_connector import send as email_send
from connectors.crm_connector import send as crm_send

def execute_with_retry(task_json, connector_func, max_retries=3):
    """
    Executes a connector function with retries and exponential backoff.

    Args:
        task_json (dict): Task data.
        connector_func (callable): The connector send function.
        max_retries (int): Maximum number of retries.

    Returns:
        dict: {"final_status": "success"|"failed", "attempts": int, "fallback_used": bool}
    """
    attempts = 0
    while attempts < max_retries:
        attempts += 1
        result = connector_func(task_json)
        if result["status"] == "success":
            return {"final_status": "success", "attempts": attempts, "fallback_used": False}
        if attempts < max_retries:
            time.sleep(2 ** (attempts - 1))  # Exponential backoff: 1s, 2s, 4s
    return {"final_status": "failed", "attempts": attempts, "fallback_used": False}

def execute_pipeline(task_json, routed_to, trace_id=None):
    """
    Executes the pipeline for a routed task, including retries and fallback.

    Args:
        task_json (dict): Task data.
        routed_to (str): The routed connector.
        trace_id (str): Trace ID from routing.

    Returns:
        dict: {"final_status": "success"|"failed", "attempts": int, "fallback_used": bool}
    """
    connector_map = {
        "calendar": calendar_send,
        "email": email_send,
        "crm": crm_send,
        "fallback": lambda x: {"status": "failed", "info": "Fallback connector - no action"}
    }

    primary_func = connector_map.get(routed_to)
    if not primary_func:
        return {"final_status": "failed", "attempts": 0, "fallback_used": False}

    # Try primary with retries
    result = execute_with_retry(task_json, primary_func)

    if result["final_status"] == "success":
        return result

    # If failed, try fallback
    fallback_map = {
        "calendar": email_send,
        "email": crm_send,
        "crm": lambda x: {"status": "failed", "info": "No fallback available"}
    }

    fallback_func = fallback_map.get(routed_to)
    if fallback_func:
        fallback_result = fallback_func(task_json)
        if fallback_result["status"] == "success":
            result["final_status"] = "success"
            result["fallback_used"] = True
        else:
            result["fallback_used"] = True

    # Update DB with final status
    task_id = task_json.get('task_id', trace_id or 'unknown')
    
    # Use Nilesh's unified DB
    import os
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nilesh', 'data', 'assistant_core.db'))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS task_execution_logs (
        task_id TEXT,
        routed_to TEXT,
        retries INTEGER,
        final_status TEXT,
        timestamp TEXT,
        trace_id TEXT
    )''')

    cursor.execute('INSERT INTO task_execution_logs (task_id, routed_to, retries, final_status, timestamp, trace_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (task_id, routed_to, result["attempts"], result["final_status"], datetime.datetime.now().isoformat(), trace_id))

    conn.commit()
    conn.close()

    return result
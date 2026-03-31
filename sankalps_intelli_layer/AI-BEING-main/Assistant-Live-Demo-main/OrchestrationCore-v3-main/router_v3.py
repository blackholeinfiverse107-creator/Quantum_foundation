import uuid
import datetime
import requests
import sqlite3
import json

def route_task(task_json):
    """
    Routes a task based on task_type, external_target, and decision from decision_hub.

    Args:
        task_json (dict): Task data, expected keys: task_id, task_type, external_target, etc.

    Returns:
        dict: Routing result with routed_to, status, trace_id, timestamp.
    """
    trace_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    task_id = task_json.get('task_id', trace_id)
    task_type = task_json.get('task_type', 'fallback')
    external_target = task_json.get('external_target', task_type)

    # Fetch decision from Nilesh's Decision Hub
    try:
        envelope = {
            'trace_id': trace_id,
            'payload': {
                'content': task_json.get('content', str(task_json)),
                'rl_reward': 0.0,
                'user_feedback': 0.0,
                'action_success': 0.0,
                'cognitive_score': 0.0,
                'confidences': {}
            }
        }
        response = requests.post('http://localhost:8000/api/decision_hub', json=envelope, timeout=5)
        response.raise_for_status()
        decision_data = response.json()['data']
        # Map to expected format
        final_decision = decision_data.get('decision', 'fallback')
        if 'task' in final_decision or 'response' in final_decision:
            decision = 'proceed'
        else:
            decision = 'defer'
        score = decision_data.get('final_score', 0.0)
        top_agent = decision_data.get('top_agent', 'unknown')
    except requests.RequestException:
        # Fallback if API fails
        decision = 'proceed'
        score = 0.0
        top_agent = 'unknown'

    if decision == 'defer':
        status = 'queued'
        routed_to = 'queue'
    else:
        status = 'sent'
        # Map to known connectors
        valid_targets = ['calendar', 'email', 'crm']
        routed_to = external_target if external_target in valid_targets else 'fallback'

    # DB Integration
    # Use Nilesh's unified DB
    import os
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'nilesh', 'data', 'assistant_core.db'))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables if not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS routing_logs (
        task_id TEXT,
        routed_to TEXT,
        status TEXT,
        trace_id TEXT,
        timestamp TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS decisions (
        task_id TEXT,
        score REAL,
        top_agent TEXT,
        decision TEXT,
        timestamp TEXT
    )''')

    # Insert routing log
    cursor.execute('INSERT INTO routing_logs (task_id, routed_to, status, trace_id, timestamp) VALUES (?, ?, ?, ?, ?)',
                   (task_id, routed_to, status, trace_id, timestamp))

    # Insert decision
    cursor.execute('INSERT INTO decisions (task_id, score, top_agent, decision, timestamp) VALUES (?, ?, ?, ?, ?)',
                   (task_id, score, top_agent, decision, timestamp))

    conn.commit()
    conn.close()

    return {
        "routed_to": routed_to,
        "status": status,
        "trace_id": trace_id,
        "timestamp": timestamp
    }
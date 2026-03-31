import sys
import os
import pytest
import sqlite3
import json
from datetime import datetime, timezone

# Add project root to path so we can import seeya and nilesh
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from seeya.contextflow_v4 import normalize_task, save_task_to_db, map_external_target
from nilesh.utils.schema import ensure_schema

# Mock DB Path for testing
TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_assistant.db'))

@pytest.fixture
def temp_db():
    """Sets up a temporary database for testing."""
    # Ensure clean state
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    
    # Initialize schema
    ensure_schema(TEST_DB_PATH)
    
    yield TEST_DB_PATH
    
    # Cleanup
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

@pytest.fixture
def mock_db_path(monkeypatch, temp_db):
    """Patches DB_PATH in contextflow_v4 and task_db_v4 to use temp_db."""
    import seeya.contextflow_v4
    import seeya.task_db_v4
    monkeypatch.setattr(seeya.contextflow_v4, 'DB_PATH', temp_db)
    monkeypatch.setattr(seeya.task_db_v4, 'DB_PATH', temp_db)
    return temp_db

def test_meeting_message_parsing():
    """Test 1: Meeting message -> task_type='meeting', target=calendar, scheduled_for parsed."""
    payload = {
        "summary_id": "s_test_1",
        "user_id": "u1",
        "platform": "whatsapp",
        "message_id": "m1",
        "summary": "Schedule a meeting with Alice tomorrow at 2 pm",
        "intent": "meeting",
        "urgency": "high",
        "entities": {},
        "context_flags": [],
        "device_context": "ios",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    task = normalize_task(payload)
    
    assert task["task_type"] == "meeting"
    assert task["external_target"] == "calendar"
    assert task["scheduled_for"] is not None
    # Verify date parsing worked (should be roughly tomorrow)
    # Just checking it's a valid ISO string is a good start
    assert "T" in task["scheduled_for"] and "Z" in task["scheduled_for"]

def test_invoice_reminder_crm():
    """Test 2: Invoice reminder -> task_type='reminder', target=crm."""
    payload = {
        "summary_id": "s_test_2",
        "user_id": "u1",
        "platform": "email",
        "message_id": "m2",
        "summary": "Send invoice to client",
        "intent": "reminder",
        "urgency": "medium",
        "entities": {},
        "context_flags": [],
        "device_context": "web",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    task = normalize_task(payload)
    
    assert task["task_type"] == "reminder"
    assert task["external_target"] == "crm"

def test_simple_follow_up_todo():
    """Test 3: Simple follow-up -> task_type='follow-up', external_target='todo'."""
    payload = {
        "summary_id": "s_test_3",
        "user_id": "u1",
        "platform": "whatsapp",
        "message_id": "m3",
        "summary": "Follow up with Bob",
        "intent": "follow_up",
        "urgency": "low",
        "entities": {},
        "context_flags": [],
        "device_context": "android",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    task = normalize_task(payload)
    
    assert task["task_type"] == "follow-up"
    assert task["external_target"] == "todo"
    # Should be None if no date mentioned
    assert task["scheduled_for"] is None

def test_db_write(mock_db_path):
    """Test 4: DB write -> row exists in tasks table."""
    task = {
        "task_id": "t_db_test",
        "user_id": "u_db",
        "summary_id": "s_db",
        "task_summary": "DB Test Task",
        "task_type": "note",
        "external_target": "none",
        "priority": "low",
        "scheduled_for": None,
        "status": "pending",
        "platform": "test",
        "device_context": "test_device",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    save_task_to_db(task)
    
    # Verify in DB
    conn = sqlite3.connect(mock_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, task_summary FROM tasks WHERE task_id = ?", (task["task_id"],))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "t_db_test"
    assert row[1] == "DB Test Task"

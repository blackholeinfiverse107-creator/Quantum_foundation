import os
import unittest
import sqlite3
import sys

# Ensure package import works for seeya.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:                                                                                                                                                
    sys.path.append(ROOT)

from seeya.contextflow_v4 import normalize_task, save_task_to_db


class TestContextFlowV4(unittest.TestCase):
    def setUp(self):
        # Ensure a clean tasks table by removing DB file if present
        self.db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'nilesh', 'data', 'assistant_core.db')
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_meeting_message_calendar_with_schedule(self):
        payload = {
            "summary_id": "s_meet_001",
            "user_id": "abc123",
            "platform": "whatsapp",
            "message_id": "m_meet_001",
            "summary": "User wants to confirm a 5 PM meeting with Priya tomorrow.",
            "intent": "confirm_meeting",
            "urgency": "medium",
            "entities": {
                "person": ["Priya"],
                "datetime": None
            },
            "context_flags": ["has_person"],
            "device_context": "ios",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["task_type"], "meeting")
        self.assertEqual(task["external_target"], "calendar")
        self.assertIsNotNone(task["scheduled_for"])

    def test_invoice_reminder_goes_to_crm(self):
        payload = {
            "summary_id": "s_inv_001",
            "user_id": "abc123",
            "platform": "email",
            "message_id": "m_inv_001",
            "summary": "Please remind client ACME about the pending invoice.",
            "intent": "reminder",
            "urgency": "high",
            "entities": {
                "person": ["ACME"],
                "datetime": None
            },
            "context_flags": ["has_person"],
            "device_context": "web",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["task_type"], "reminder")
        self.assertEqual(task["external_target"], "crm")

    def test_follow_up_without_date_goes_to_todo(self):
        payload = {
            "summary_id": "s_fu_001",
            "user_id": "abc123",
            "platform": "sms",
            "message_id": "m_fu_001",
            "summary": "Please follow up with Ajay regarding the proposal.",
            "intent": "follow_up",
            "urgency": "low",
            "entities": {
                "person": ["Ajay"],
                "datetime": None
            },
            "context_flags": ["has_person"],
            "device_context": "android",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["task_type"], "follow-up")
        self.assertIsNone(task["scheduled_for"])
        self.assertEqual(task["external_target"], "todo")

    def test_db_write_row_exists_in_tasks(self):
        payload = {
            "summary_id": "s_db_001",
            "user_id": "abc123",
            "platform": "instagram",
            "message_id": "m_db_001",
            "summary": "Confirm call with Dan next Monday at 10am.",
            "intent": "meeting",
            "urgency": "medium",
            "entities": {
                "person": ["Dan"],
                "datetime": None
            },
            "context_flags": ["has_person"],
            "device_context": "android",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        save_task_to_db(task)
        self.assertTrue(os.path.exists(self.db_path))

        conn = sqlite3.connect(self.db_path)
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT task_id, user_id, summary_id, task_summary, task_type, external_target, status FROM tasks WHERE task_id = ?",
                (task["task_id"],),
            )
            row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["task_id"], task["task_id"])
            self.assertEqual(row["user_id"], task["user_id"])
            self.assertEqual(row["summary_id"], task["summary_id"])
            self.assertEqual(row["task_type"], "meeting")
            self.assertEqual(row["status"], "pending")
        finally:
            conn.close()

    def test_intent_normalization_confirm_meeting(self):
        payload = {
            "summary_id": "s_norm_001",
            "user_id": "abc123",
            "platform": "whatsapp",
            "message_id": "m_norm_001",
            "summary": "Please confirm the meeting with Priya.",
            "intent": "confirm_meeting",
            "urgency": "low",
            "entities": {
                "person": ["Priya"],
                "datetime": None
            },
            "context_flags": ["has_person"],
            "device_context": "ios",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["task_type"], "meeting")

    def test_priority_escalation_with_urgent_text(self):
        payload = {
            "summary_id": "s_pri_urgent",
            "user_id": "abc123",
            "platform": "email",
            "message_id": "m_pri_urgent",
            "summary": "This is urgent and needs attention ASAP.",
            "intent": "note",
            "urgency": "low",
            "entities": {
                "person": [],
                "datetime": None
            },
            "context_flags": [],
            "device_context": "web",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["priority"], "high")

    def test_priority_meeting_within_24h(self):
        from datetime import datetime, timedelta
        soon = (datetime.utcnow() + timedelta(hours=2)).replace(microsecond=0).isoformat() + "Z"
        payload = {
            "summary_id": "s_pri_meet",
            "user_id": "abc123",
            "platform": "sms",
            "message_id": "m_pri_meet",
            "summary": "Meeting with Alex in 2 hours.",
            "intent": "meeting",
            "urgency": "medium",
            "entities": {
                "person": ["Alex"],
                "datetime": soon
            },
            "context_flags": ["has_date", "has_person"],
            "device_context": "android",
            "generated_at": "2025-11-20T14:00:02Z"
        }
        task = normalize_task(payload)
        self.assertEqual(task["task_type"], "meeting")
        self.assertEqual(task["priority"], "high")


if __name__ == "__main__":
    unittest.main()

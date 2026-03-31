import logging
import random

logging.basicConfig(level=logging.INFO)

def send(task_json):
    """
    Sends a task to the CRM connector.

    Args:
        task_json (dict): Task data.

    Returns:
        dict: {"status": "success"|"failed", "info": "..."}
    """
    if not isinstance(task_json, dict):
        return {"status": "failed", "info": "Invalid input: task_json must be dict"}

    logging.info(f"Attempting to send CRM task: {task_json}")

    # Simulate success/failure
    success = random.choice([True, False])
    if success:
        status = "success"
        info = "CRM record updated successfully"
    else:
        status = "failed"
        info = "Failed to update CRM record"

    return {"status": status, "info": info}
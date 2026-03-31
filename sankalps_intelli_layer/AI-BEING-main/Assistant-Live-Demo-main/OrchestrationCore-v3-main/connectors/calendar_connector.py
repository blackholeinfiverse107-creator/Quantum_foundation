import logging
import random

logging.basicConfig(level=logging.INFO)

def send(task_json):
    """
    Sends a task to the calendar connector.

    Args:
        task_json (dict): Task data.

    Returns:
        dict: {"status": "success"|"failed", "info": "..."}
    """
    if not isinstance(task_json, dict):
        return {"status": "failed", "info": "Invalid input: task_json must be dict"}

    logging.info(f"Attempting to send calendar task: {task_json}")

    # Simulate success/failure
    success = random.choice([True, False])
    if success:
        status = "success"
        info = "Event added to calendar"
    else:
        status = "failed"
        info = "Failed to add event to calendar"

    return {"status": status, "info": info}
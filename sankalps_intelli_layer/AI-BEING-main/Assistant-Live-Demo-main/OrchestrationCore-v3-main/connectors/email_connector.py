import logging
import random

logging.basicConfig(level=logging.INFO)

def send(task_json):
    """
    Sends a task to the email connector.

    Args:
        task_json (dict): Task data.

    Returns:
        dict: {"status": "success"|"failed", "info": "..."}
    """
    if not isinstance(task_json, dict):
        return {"status": "failed", "info": "Invalid input: task_json must be dict"}

    logging.info(f"Attempting to send email task: {task_json}")

    # Simulate success/failure
    success = random.choice([True, False])
    if success:
        status = "success"
        info = "Email sent successfully"
    else:
        status = "failed"
        info = "Failed to send email"

    return {"status": status, "info": info}
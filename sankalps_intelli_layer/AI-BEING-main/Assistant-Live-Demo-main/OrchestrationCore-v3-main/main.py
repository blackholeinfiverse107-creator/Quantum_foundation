import sys
import os
from datetime import datetime
from fastapi import FastAPI
from router_v3 import route_task
from pipeline_controls import execute_pipeline

# Add seeya to path for summaryflow integration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from seeya.summaryflow_v3 import summarize_message

# Placeholder for embedding if module is missing
try:
    from seeya.embedcore_v3 import generate_embedding
except ImportError:
    def generate_embedding(text): return [0.0] * 384

# Function to create task via Sankalp's ContextFlow
def create_task_via_contextflow(summary_payload: dict):
    import requests
    # ContextFlow running on port 8000
    response = requests.post('http://localhost:8000/api/contextflow_task', json=summary_payload, timeout=5)
    response.raise_for_status()
    # ContextFlow returns {status, timestamp, trace_id, data: TaskObject}
    return response.json().get('data')

# Function to send routing results to Yash's frontend
def send_to_yash_frontend(routing_result: dict, pipeline_result: dict = None):
    # Mock implementation for now
    print(f"Sending to Frontend: {routing_result}")

app = FastAPI(title="OrchestratorCore v3", description="Multi-Connector Pipeline + External Routing Engine")

@app.post("/orchestrate")
async def orchestrate_task(request: dict):
    """
    Orchestrate a task: Summarize -> ContextFlow (Create Task) -> Route -> Execute.

    Input: {"message_text": "...", "user_id": "...", "platform": "..."} 
           OR Pre-computed Summary JSON
    Output: {"routing": routing_result, "pipeline": pipeline_result or None, "task": task_object}
    """
    
    # 1. Summarize if needed
    if "summary" not in request or "intent" not in request:
        # Assume raw message input
        payload = {
            "user_id": request.get('user_id', 'unknown'),
            "platform": request.get('platform', 'orchestrator'),
            "message_id": request.get('message_id', f"m_{int(datetime.now().timestamp())}"),
            "message_text": request.get('message_text', ''),
            "timestamp": request.get('timestamp', datetime.now().isoformat())
        }
        summary_payload = summarize_message(payload)
    else:
        summary_payload = request

    # 2. Create Task via ContextFlow
    try:
        task_object = create_task_via_contextflow(summary_payload)
        if not task_object:
            return {"error": "ContextFlow returned no task data"}
    except Exception as e:
        return {"error": f"Failed to create task via ContextFlow: {str(e)}"}

    # 3. Generate embedding (optional)
    try:
        embedding = generate_embedding(task_object.get('task_summary', ''))
        task_object['embedding'] = embedding
    except Exception as e:
        print(f"Embedding generation failed: {e}")

    # 4. Route
    routing_result = route_task(task_object)
    
    # 5. Execute
    if routing_result["status"] == "sent":
        pipeline_result = execute_pipeline(task_object, routing_result["routed_to"], routing_result["trace_id"])
        result = {"routing": routing_result, "pipeline": pipeline_result, "task": task_object}
    else:
        pipeline_result = None
        result = {"routing": routing_result, "pipeline": None, "task": task_object}

    # 6. Send results to Frontend
    send_to_yash_frontend(routing_result, pipeline_result)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
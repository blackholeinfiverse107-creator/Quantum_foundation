from fastapi import APIRouter
from pydantic import BaseModel
import os
import sys
import re
from typing import Tuple, Optional
from ..core.llm_bridge import llm_bridge
from ..core.arl_messaging import message_for
from ..core.assistant_orchestrator import sanitize_text
from ..core.logging import get_logger
from ..core.bhiv_core import BHIVCore
from ..core.bhiv_reasoner import BHIVReasoner
from ..memory.memory_manager import MemoryManager
from ..agents.planner_agent import PlannerAgent
from ..agents.researcher_agent import ResearcherAgent
from ..agents.analyst_agent import AnalystAgent
from ..agents.executor_agent import ExecutorAgent
from ..agents.evaluator_agent import EvaluatorAgent
from ..tools.search_tool import SearchTool
from ..tools.web_browser_tool import WebBrowserTool
from ..tools.calculator_tool import CalculatorTool
from ..tools.file_tool import FileTool
from ..tools.automation_tool import AutomationTool
from ..core.sankalp.engine import SankalpEngine

router = APIRouter()
logger = get_logger(__name__)
# Initialize Sankalp Engine
sankalp_engine = SankalpEngine()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)
try:
    from raj.execution_gateway import execution_gateway as raj_execution_gateway
except Exception:
    raj_execution_gateway = None

# Initialize BHIV components
memory_manager = MemoryManager()
agents = {
    "planner": PlannerAgent(),
    "researcher": ResearcherAgent(),
    "analyst": AnalystAgent(),
    "executor": ExecutorAgent(),
    "evaluator": EvaluatorAgent()
}
tools = {
    "search": SearchTool(),
    "web_browser": WebBrowserTool(),
    "calculator": CalculatorTool(),
    "file": FileTool(),
    "automation": AutomationTool()
}
reasoner = BHIVReasoner()
bhiv = BHIVCore(memory_manager, agents, tools, reasoner)

class RespondRequest(BaseModel):
    query: str
    context: dict = {}
    model: str = "uniguru"
    decision: str = "respond"

@router.post("/respond")
async def generate_response(request: RespondRequest):
    try:
        if request.decision == "bhiv_core":
            return await bhiv.process(request)
        prompt = f"Context: {request.context}\nQuery: {request.query}\nProvide a helpful response."
        response = await llm_bridge.call_llm(request.model, prompt)
        
        # Sankalp Engine Integration
        result = sankalp_engine.process_response(request.query, response, request.context)
        
        logger.info(
            "Sankalp processed response",
            extra={"extra_fields": {
                "decision": result.get("decision"),
                "trace_id": result.get("trace_id"),
                "endpoint": "/api/respond"
            }}
        )
        
        return {"response": result["response"], "trace_id": result["trace_id"]}

    except Exception as e:
        return {"error": f"Failed to generate response: {str(e)}"}

def arl_gate(text: str, platform: str) -> Tuple[str, Optional[str]]:
    try:
        if not raj_execution_gateway:
            return "ALLOW", None
        platform_policy = (platform or "web").upper()
        result = raj_execution_gateway(
            intent=text,
            emotional_output={"tone": "neutral", "dependency_score": 0.0},
            age_gate_status="ALLOWED",
            region_policy="IN",
            platform_policy=platform_policy,
            karma_score=0.0,
            risk_flags=[]
        )
        return result.get("decision", "ALLOW"), result.get("rewrite_class")
    except Exception:
        return "ALLOW", None

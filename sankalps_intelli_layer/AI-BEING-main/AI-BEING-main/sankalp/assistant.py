from typing import Dict, Any
from intelligence_core.core import IntelligenceCore
from .adapter import IntelligenceAdapter
from .engine import ResponseComposerEngine

class Assistant:
    def __init__(self):
        self.brain = IntelligenceCore()
        self.engine = ResponseComposerEngine()

    def respond(self, message: str, user_context: Dict[str, Any], karma_data: Dict[str, Any], bucket_data: Dict[str, Any]) -> Dict[str, Any]:
        intel_output, _ = self.brain.process_interaction(user_context, karma_data, bucket_data, message_content=message)
        sankalp_input = IntelligenceAdapter.adapt(
            embodiment_output=intel_output,
            original_context=user_context,
            original_karma=karma_data,
            message_content=message,
            context_summary="Assistant interaction"
        )
        response_block = self.engine.process(sankalp_input)
        return response_block.to_dict()

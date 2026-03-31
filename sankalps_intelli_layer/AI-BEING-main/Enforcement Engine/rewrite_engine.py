from models.rewrite_guidance import RewriteGuidance

REWRITE_MAP = {
    "EMOTIONAL_DEPENDENCY_RISK": RewriteGuidance(
        rewrite_class="REDUCE_EMOTIONAL_DEPENDENCY",
        rewrite_hints=[
            "avoid exclusivity",
            "encourage autonomy",
            "neutral supportive tone"
        ]
    ),
    "MANIPULATIVE_BEHAVIOR_DETECTED": RewriteGuidance(
        rewrite_class="REMOVE_MANIPULATION",
        rewrite_hints=[
            "remove pressure framing",
            "avoid guilt language"
        ]
    ),
    "PLATFORM_POLICY_REWRITE": RewriteGuidance(
        rewrite_class="PLATFORM_SAFE_REWRITE",
        rewrite_hints=[
            "remove disallowed phrasing",
            "comply with platform norms"
        ]
    )
    ,
    "LOW_KARMA_CONFIDENCE": RewriteGuidance(
        rewrite_class="CONFIDENCE_SUPPORTIVE_TONE",
        rewrite_hints=[
            "use steady, non-hyped language",
            "affirm without dependency",
            "prefer clarity over persuasion"
        ]
    )
}

def generate_rewrite_guidance(evaluator_results):
    for result in evaluator_results:
        if result.triggered and result.code in REWRITE_MAP:
            return REWRITE_MAP[result.code]
    return None

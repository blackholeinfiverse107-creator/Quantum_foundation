from .age_compliance import AgeComplianceEvaluator
from .region_restriction import RegionRestrictionEvaluator
from .platform_policy import PlatformPolicyEvaluator
from .safety_risk import SafetyRiskEvaluator
from .dependency_tone import DependencyToneEvaluator
from .sexual_escalation import SexualEscalationEvaluator
from .emotional_manipulation import EmotionalManipulationEvaluator
from .karma_confidence import KarmaConfidenceEvaluator

ALL_EVALUATORS = [
    AgeComplianceEvaluator(),
    RegionRestrictionEvaluator(),
    PlatformPolicyEvaluator(),
    SafetyRiskEvaluator(),
    DependencyToneEvaluator(),
    SexualEscalationEvaluator(),
    EmotionalManipulationEvaluator(),
    KarmaConfidenceEvaluator(),
]

#!/usr/bin/env python3
"""
AUTOMATED VALIDATION SUITE v2.0 - COMPLETE UPGRADE
Comprehensive content safety validation with full traceability
"""

import json
import re
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration constants"""
    APP_NAME = "Auto Validation Suite v2.0"
    LOG_FILE = "validation_logs.json"
    DEBUG_LOG = "validation_debug.log"
    TEST_MATRIX_FILE = "edge_test_matrix.json"
    VERSION = "2.0.0"
    
    # Confidence thresholds
    BLOCK_THRESHOLD = 0.7
    FLAG_THRESHOLD = 0.4
    HIGH_CONFIDENCE = 0.8
    
    # Response codes
    SUCCESS = 0
    ERROR = 1

# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class RiskCategory(str, Enum):
    """All risk categories for validation"""
    EMOTIONAL_BAIT = "emotional_dependency_bait"
    SEXUAL_ESCALATION = "sexual_escalation_attempt"
    MANIPULATIVE_PHRASING = "manipulative_phrasing"
    REGION_CONFLICT = "region_platform_conflict"
    YOUTH_RISK = "youth_risk_behavior"
    LONELINESS_HOOK = "loneliness_hook"
    ILLEGAL_INTENT = "illegal_intent_probing"
    
class Decision(str, Enum):
    """Validation decisions"""
    PASS = "pass"
    FLAG = "flag"
    BLOCK = "block"
    
class ReasonCode(str, Enum):
    """Detailed reason codes for validation results"""
    CLEAN = "clean_content"
    EMOTIONAL_MANIPULATION = "emotional_manipulation_detected"
    SEXUAL_CONTENT = "sexual_escalation_detected"
    MANIPULATIVE_LANGUAGE = "manipulative_phrasing_detected"
    REGION_VIOLATION = "region_platform_conflict_detected"
    YOUTH_EXPLOITATION = "youth_risk_behavior_detected"
    LONELINESS_EXPLOIT = "loneliness_hook_detected"
    ILLEGAL_PROBING = "illegal_intent_probing_detected"
    VIOLENT_THREAT = "violent_threat_detected"
    SELF_HARM_RISK = "self_harm_risk_detected"
    MULTIPLE_VIOLATIONS = "multiple_violations_detected"
    SYSTEM_ERROR = "system_error_detected"

@dataclass
class ValidationResult:
    """Structured validation result"""
    decision: Decision
    reason_code: ReasonCode
    trace_id: str
    risk_category: RiskCategory
    confidence: float
    matched_patterns: List[str]
    matched_text: List[str]
    explanation: str
    severity: str = "medium"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "decision": self.decision.value,
            "reason_code": self.reason_code.value,
            "trace_id": self.trace_id,
            "risk_category": self.risk_category.value,
            "confidence": round(self.confidence, 3),
            "matched_patterns": self.matched_patterns[:5],  # Limit output
            "matched_text": self.matched_text[:5],  # Limit output
            "explanation": self.explanation,
            "severity": self.severity,
            "timestamp": datetime.utcnow().isoformat()
        }

@dataclass
class ValidationRequest:
    """Complete validation request"""
    content: str
    metadata: Dict[str, Any]
    request_id: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "request_id": self.request_id,
            "timestamp": self.timestamp
        }

@dataclass 
class ValidationResponse:
    """Complete validation response"""
    request_id: str
    overall_decision: Decision
    summary_flag: str
    results: List[ValidationResult]
    metrics: Dict[str, Any]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "overall_decision": self.overall_decision.value,
            "summary_flag": self.summary_flag,
            "results": [r.to_dict() for r in self.results],
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }

# ============================================================================
# COMPREHENSIVE PATTERN LIBRARY
# ============================================================================

class PatternLibrary:
    """Comprehensive pattern library for all risk categories"""
    
    # Emotional dependency bait patterns
    EMOTIONAL_BAIT = [
        (r'\bi\s+need\s+you\b', 'i need you'),
        (r'\byou\'?re\s+the\s+only\s+one\b', 'you are the only one'),
        (r'\bcan\'?t\s+live\s+without\s+you\b', 'cannot live without you'),
        (r'\byou\s+complete\s+me\b', 'you complete me'),
        (r'\bmy\s+everything\b', 'my everything'),
        (r'\bsoul\W?mate\b', 'soulmate'),
        (r'\byou\s+understand\s+me\b', 'you understand me'),
        (r'\bno\s+one\s+else\s+gets\s+me\b', 'no one else gets me'),
        (r'\byou\'?re\s+special\b', 'you are special'),
        (r'\bi\s+trust\s+only\s+you\b', 'i trust only you'),
        (r'\bmy\s+confidant\b', 'my confidant'),
        (r'\bsave\s+me\b', 'save me'),
        (r'\byou\'?re\s+my\s+reason\b', 'you are my reason'),
        (r'\bwithout\s+you\s+i\'?m\s+nothing\b', 'without you i am nothing')
    ]
    
    # Sexual escalation patterns
    SEXUAL_ESCALATION = [
        (r'\bsend\s+(me\s+)?nudes?\b', 'send nudes'),
        (r'\bsend\s+(me\s+)?(sexy|naked)\s+pics?\b', 'send sexy pics'),
        (r'\bshow\s+(me\s+)?your\b', 'show me your'),
        (r'\btouch\s+(yourself|me)\b', 'touch yourself/me'),
        (r'\bhorny\b', 'horny'),
        (r'\baroused?\b', 'aroused'),
        (r'\bsexting\b', 'sexting'),
        (r'\bprivate\s+parts\b', 'private parts'),
        (r'\bundress\b', 'undress'),
        (r'\bget\s+naked\b', 'get naked'),
        (r'\bsexual\b', 'sexual'),
        (r'\berotic\b', 'erotic'),
        (r'\bintimate\s+pics?\b', 'intimate pics'),
        (r'\bbedroom\s+stuff\b', 'bedroom stuff'),
        (r'\bnaughty\s+pics?\b', 'naughty pics'),
        (r'\bexplicit\s+content\b', 'explicit content')
    ]
    
    # Manipulative phrasing patterns
    MANIPULATIVE_PHRASING = [
        (r'\bif\s+you\s+(really\s+)?(loved|cared\s+about)\s+me\b', 'if you loved me'),
        (r'\bprove\s+you\s+care\b', 'prove you care'),
        (r'\breal\s+friends\s+would\b', 'real friends would'),
        (r'\beveryone\s+else\s+does\b', 'everyone else does'),
        (r'\byou\s+owe\s+me\b', 'you owe me'),
        (r'\bafter\s+all\s+i\'?ve\s+done\b', 'after all i have done'),
        (r'\bdon\'?t\s+you\s+trust\s+me\b', 'don\'t you trust me'),
        (r'\bi\s+thought\s+you\s+were\s+different\b', 'i thought you were different'),
        (r'\bi\'?ll\s+be\s+(hurt|upset)\s+if\b', 'i will be hurt if'),
        (r'\bguilt\W?trip\b', 'guilt trip'),
        (r'\bemotional\W?blackmail\b', 'emotional blackmail'),
        (r'\bmanipulat\b', 'manipulat'),
        (r'\byou\'?re\s+making\s+me\s+feel\b', 'you are making me feel')
    ]
    
    # Youth risk behavior patterns
    YOUTH_RISK = [
        (r'\bmeet\s+(up|alone)\b', 'meet up/alone'),
        (r'\bskip\s+(school|class)\b', 'skip school/class'),
        (r'\brun\s+away\b', 'run away'),
        (r'\bdon\'?t\s+tell\s+(your\s+)?(parents|mom|dad)\b', 'don\'t tell parents'),
        (r'\bour\s+secret\b', 'our secret'),
        (r'\bhidden\s+relationship\b', 'hidden relationship'),
        (r'\bage\s+gap\b', 'age gap'),
        (r'\bold(er)?\s+man\b', 'older man'),
        (r'\bunderage\b', 'underage'),
        (r'\bsend\s+(your\s+)?location\b', 'send location'),
        (r'\bdelete\s+messages\b', 'delete messages'),
        (r'\bkeep\s+this\s+between\s+us\b', 'keep this between us'),
        (r'\bno\s+one\s+needs\s+to\s+know\b', 'no one needs to know'),
        (r'\bminor\b', 'minor'),
        (r'\bgrooming\b', 'grooming'),
        (r'\bexploit\b', 'exploit')
    ]
    
    # Loneliness hook patterns
    LONELINESS_HOOK = [
        (r'\bno\s+one\s+likes\s+me\b', 'no one likes me'),
        (r'\ball\s+alone\b', 'all alone'),
        (r'\bforever\s+alone\b', 'forever alone'),
        (r'\bno\s+friends\b', 'no friends'),
        (r'\bisolated\b', 'isolated'),
        (r'\blonely\b', 'lonely'),
        (r'\balways\s+by\s+myself\b', 'always by myself'),
        (r'\bsocially\s+awkward\b', 'socially awkward'),
        (r'\bcan\'?t\s+make\s+friends\b', 'cannot make friends'),
        (r'\brejected\b', 'rejected'),
        (r'\bunloved\b', 'unloved'),
        (r'\bnobody\s+cares\b', 'nobody cares'),
        (r'\bi\'?m\s+so\s+lonely\b', 'i am so lonely'),
        (r'\bfeel\s+empty\b', 'feel empty')
    ]
    
    # VIOLENT AND ILLEGAL INTENT PATTERNS - COMPREHENSIVE
    VIOLENT_INTENT = [
        # Murder and killing
        (r'\b(kill|murder|assassinat|execute|eliminat)\s+(my\s+)?(sister|brother|mother|father|parent|wife|husband|girlfriend|boyfriend|friend)\b', 'kill family/friend'),
        (r'\b(kill|murder|assassinat|execute|eliminat)\s+(someone|a\s+person|people|them|him|her)\b', 'kill someone'),
        (r'\b(kill|murder|assassinat)\s+myself\b', 'kill myself'),
        (r'\bplot\s+to\s+(kill|murder)\b', 'plot to kill'),
        (r'\bplan\s+to\s+(kill|murder)\b', 'plan to kill'),
        (r'\bwant\s+to\s+(kill|murder)\b', 'want to kill'),
        (r'\bgoing\s+to\s+(kill|murder)\b', 'going to kill'),
        (r'\bwill\s+(kill|murder)\b', 'will kill'),
        
        # Bomb and explosive threats
        (r'\bbomb\s+(the|this|that|a)\s+(building|school|office|airport|station|place)\b', 'bomb a building'),
        (r'\bblow\s+up\s+(the|this|that|a)\s+(building|school|office|place)\b', 'blow up a building'),
        (r'\bexplosive\s+(device|bomb)\b', 'explosive device'),
        (r'\bplant\s+a\s+bomb\b', 'plant a bomb'),
        (r'\bdetonate\s+a\s+bomb\b', 'detonate a bomb'),
        
        # Shooting threats
        (r'\bshoot\s+(someone|people|a\s+person|them|him|her)\b', 'shoot someone'),
        (r'\bshoot\s+up\s+(the|this|that|a)\s+(school|place|building)\b', 'shoot up a place'),
        (r'\bopen\s+fire\b', 'open fire'),
        (r'\bgun\s+violence\b', 'gun violence'),
        (r'\buse\s+a\s+gun\b', 'use a gun'),
        
        # General violence
        (r'\battack\s+(someone|people|a\s+person)\b', 'attack someone'),
        (r'\bassault\s+(someone|people|a\s+person)\b', 'assault someone'),
        (r'\bstab\s+(someone|people|a\s+person)\b', 'stab someone'),
        (r'\bharm\s+(someone|people|a\s+person|myself)\b', 'harm someone'),
        (r'\bhurt\s+(someone|people|a\s+person|myself)\b', 'hurt someone'),
        (r'\bviolence\s+against\b', 'violence against'),
        
        # Suicide and self-harm
        (r'\bsuicide\b', 'suicide'),
        (r'\bcommit\s+suicide\b', 'commit suicide'),
        (r'\bend\s+my\s+life\b', 'end my life'),
        (r'\btake\s+my\s+life\b', 'take my life'),
        (r'\bself\W?harm\b', 'self-harm'),
        (r'\bself\W?injur\b', 'self-injury'),
        (r'\bcut\s+myself\b', 'cut myself'),
        (r'\bwant\s+to\s+die\b', 'want to die'),
        (r'\bdepressed\s+and\s+suicidal\b', 'depressed and suicidal'),
        
        # Terrorist activities
        (r'\bterrorist\s+attack\b', 'terrorist attack'),
        (r'\bterrorist\s+plot\b', 'terrorist plot'),
        (r'\bextremist\s+activity\b', 'extremist activity'),
        
        # Kidnapping and abduction
        (r'\bkidnap\b', 'kidnap'),
        (r'\babduct\b', 'abduct'),
        (r'\btake\s+hostage\b', 'take hostage'),
        
        # Arson
        (r'\bburn\s+down\b', 'burn down'),
        (r'\bset\s+fire\s+to\b', 'set fire to'),
        (r'\barson\b', 'arson')
    ]
    
    # Illegal activities patterns
    ILLEGAL_ACTIVITIES = [
        # Drugs
        (r'\bbuy\s+drugs\b', 'buy drugs'),
        (r'\bsell\s+drugs\b', 'sell drugs'),
        (r'\bpurchase\s+drugs\b', 'purchase drugs'),
        (r'\bget\s+drugs\b', 'get drugs'),
        (r'\bdrug\s+deal\b', 'drug deal'),
        (r'\billegal\s+drugs\b', 'illegal drugs'),
        
        # Fraud and theft
        (r'\bhack\s+(into\s+)?(an\s+)?account\b', 'hack account'),
        (r'\bsteal\s+(data|information|money)\b', 'steal data/money'),
        (r'\bcredit\s+card\s+fraud\b', 'credit card fraud'),
        (r'\bidentity\s+theft\b', 'identity theft'),
        (r'\bphishing\b', 'phishing'),
        (r'\bscam\b', 'scam'),
        
        # Child exploitation
        (r'\bchild\s+porn\b', 'child porn'),
        (r'\bchild\s+abuse\b', 'child abuse'),
        (r'\bunderage\s+sexual\b', 'underage sexual'),
        (r'\bminor\s+exploitation\b', 'minor exploitation'),
        
        # Human trafficking
        (r'\bhuman\s+trafficking\b', 'human trafficking'),
        (r'\bsell\s+(a\s+)?person\b', 'sell a person'),
        (r'\btraffic\s+people\b', 'traffic people'),
        
        # Weapons
        (r'\bbuy\s+(a\s+)?gun\b', 'buy a gun'),
        (r'\bpurchase\s+(a\s+)?weapon\b', 'purchase weapon'),
        (r'\bweapon\s+deal\b', 'weapon deal'),
        
        # Fake documents
        (r'\bfake\s+id\b', 'fake id'),
        (r'\bfake\s+passport\b', 'fake passport'),
        (r'\bfake\s+document\b', 'fake document')
    ]
    
    # Region and platform patterns
    REGION_CONFLICTS = {
        "china": ["twitter banned", "facebook blocked", "youtube restricted", "google censored"],
        "eu": ["gdpr violation", "data protection breach", "cookie law"],
        "us": ["hipaa violation", "ferpa violation", "first amendment"],
        "iran": ["whatsapp banned", "instagram blocked", "social media ban"],
        "north_korea": ["internet access", "social media", "western media"]
    }

# ============================================================================
# BASE VALIDATOR WITH COMPLETE FUNCTIONALITY
# ============================================================================

class BaseValidator:
    """Base validator with complete functionality"""
    
    def __init__(self, risk_category: RiskCategory):
        self.risk_category = risk_category
        self.trace_id = f"{risk_category.value[:3]}_{str(uuid.uuid4())[:6]}"
        self.patterns = []
        
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        """Main validation method - to be implemented by subclasses"""
        raise NotImplementedError
    
    def _find_matches(self, content: str, pattern_list: List[tuple]) -> tuple:
        """Find pattern matches in content"""
        matches = []
        matched_texts = []
        
        for pattern, description in pattern_list:
            found = re.finditer(pattern, content, re.IGNORECASE)
            for match in found:
                matches.append(description)
                matched_texts.append(match.group(0))
        
        return matches, matched_texts
    
    def _calculate_confidence(self, match_count: int, base_confidence: float = 0.5) -> float:
        """Calculate confidence score"""
        return min(base_confidence + (match_count * 0.15), 0.99)
    
    def _create_pass_result(self, confidence: float = 0.95) -> ValidationResult:
        """Create a pass result"""
        return ValidationResult(
            decision=Decision.PASS,
            reason_code=ReasonCode.CLEAN,
            trace_id=self.trace_id,
            risk_category=self.risk_category,
            confidence=confidence,
            matched_patterns=[],
            matched_text=[],
            explanation=f"No {self.risk_category.value.replace('_', ' ')} detected"
        )
    
    def _create_flag_result(self, matches: List[str], matched_texts: List[str], 
                           reason_code: ReasonCode, base_confidence: float = 0.4) -> ValidationResult:
        """Create a flag result"""
        return ValidationResult(
            decision=Decision.FLAG,
            reason_code=reason_code,
            trace_id=self.trace_id,
            risk_category=self.risk_category,
            confidence=self._calculate_confidence(len(matches), base_confidence),
            matched_patterns=matches[:5],
            matched_text=matched_texts[:5],
            explanation=f"Detected {len(matches)} pattern(s): {', '.join(matches[:3])}"
        )
    
    def _create_block_result(self, matches: List[str], matched_texts: List[str],
                            reason_code: ReasonCode, base_confidence: float = 0.6) -> ValidationResult:
        """Create a block result"""
        return ValidationResult(
            decision=Decision.BLOCK,
            reason_code=reason_code,
            trace_id=self.trace_id,
            risk_category=self.risk_category,
            confidence=self._calculate_confidence(len(matches), base_confidence),
            matched_patterns=matches[:5],
            matched_text=matched_texts[:5],
            explanation=f"Detected {len(matches)} high-risk pattern(s): {', '.join(matches[:3])}",
            severity="high"
        )

# ============================================================================
# SPECIFIC VALIDATOR IMPLEMENTATIONS
# ============================================================================

class EmotionalBaitValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.EMOTIONAL_BAIT)
        self.patterns = PatternLibrary.EMOTIONAL_BAIT
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        matches, matched_texts = self._find_matches(content, self.patterns)
        
        if matches:
            return self._create_flag_result(
                matches, matched_texts, ReasonCode.EMOTIONAL_MANIPULATION, 0.4
            )
        
        return self._create_pass_result(0.95)

class SexualEscalationValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.SEXUAL_ESCALATION)
        self.patterns = PatternLibrary.SEXUAL_ESCALATION
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        matches, matched_texts = self._find_matches(content, self.patterns)
        
        if matches:
            return self._create_block_result(
                matches, matched_texts, ReasonCode.SEXUAL_CONTENT, 0.6
            )
        
        return self._create_pass_result(0.92)

class ManipulativePhrasingValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.MANIPULATIVE_PHRASING)
        self.patterns = PatternLibrary.MANIPULATIVE_PHRASING
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        matches, matched_texts = self._find_matches(content, self.patterns)
        
        if matches:
            return self._create_flag_result(
                matches, matched_texts, ReasonCode.MANIPULATIVE_LANGUAGE, 0.4
            )
        
        return self._create_pass_result(0.90)

class YouthRiskValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.YOUTH_RISK)
        self.patterns = PatternLibrary.YOUTH_RISK
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        matches, matched_texts = self._find_matches(content, self.patterns)
        
        if matches:
            user_age = metadata.get("user_age")
            if user_age and user_age < 18:
                return self._create_block_result(
                    matches, matched_texts, ReasonCode.YOUTH_EXPLOITATION, 0.7
                )
            else:
                return self._create_flag_result(
                    matches, matched_texts, ReasonCode.YOUTH_EXPLOITATION, 0.5
                )
        
        return self._create_pass_result(0.88)

class LonelinessHookValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.LONELINESS_HOOK)
        self.patterns = PatternLibrary.LONELINESS_HOOK
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        matches, matched_texts = self._find_matches(content, self.patterns)
        
        if matches:
            return self._create_flag_result(
                matches, matched_texts, ReasonCode.LONELINESS_EXPLOIT, 0.4
            )
        
        return self._create_pass_result(0.87)

class IllegalIntentValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.ILLEGAL_INTENT)
        self.violent_patterns = PatternLibrary.VIOLENT_INTENT
        self.illegal_patterns = PatternLibrary.ILLEGAL_ACTIVITIES
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        # Check for violent intent
        violent_matches, violent_texts = self._find_matches(content, self.violent_patterns)
        
        # Check for illegal activities
        illegal_matches, illegal_texts = self._find_matches(content, self.illegal_patterns)
        
        # Combine results
        all_matches = violent_matches + illegal_matches
        all_texts = violent_texts + illegal_texts
        
        if all_matches:
            # Determine severity
            has_violent = len(violent_matches) > 0
            has_suicide = any('suicide' in m.lower() or 'kill myself' in m.lower() for m in all_matches)
            has_murder = any('kill' in m.lower() and 'myself' not in m.lower() for m in all_matches)
            
            if has_suicide:
                return ValidationResult(
                    decision=Decision.BLOCK,
                    reason_code=ReasonCode.SELF_HARM_RISK,
                    trace_id=self.trace_id,
                    risk_category=self.risk_category,
                    confidence=self._calculate_confidence(len(all_matches), 0.8),
                    matched_patterns=all_matches[:5],
                    matched_text=all_texts[:5],
                    explanation=f"⚠️ SELF-HARM RISK: Detected suicidal content: {', '.join(all_matches[:3])}",
                    severity="critical"
                )
            elif has_murder or has_violent:
                return ValidationResult(
                    decision=Decision.BLOCK,
                    reason_code=ReasonCode.VIOLENT_THREAT,
                    trace_id=self.trace_id,
                    risk_category=self.risk_category,
                    confidence=self._calculate_confidence(len(all_matches), 0.75),
                    matched_patterns=all_matches[:5],
                    matched_text=all_texts[:5],
                    explanation=f"🚨 VIOLENT THREAT: Detected {len(all_matches)} violent/intent pattern(s)",
                    severity="high"
                )
            else:
                return self._create_block_result(
                    all_matches, all_texts, ReasonCode.ILLEGAL_PROBING, 0.6
                )
        
        return self._create_pass_result(0.94)

class RegionConflictValidator(BaseValidator):
    def __init__(self):
        super().__init__(RiskCategory.REGION_CONFLICT)
    
    def validate(self, content: str, metadata: Dict) -> ValidationResult:
        user_region = metadata.get("user_region", "").lower()
        platform = metadata.get("platform", "").lower()
        
        conflicts = []
        conflict_texts = []
        
        # Check platform-region conflicts
        if user_region:
            if "china" in user_region and any(p in platform for p in ["twitter", "facebook", "youtube"]):
                conflicts.append("Western platform in China")
                conflict_texts.append(f"{platform} in China")
            
            if "iran" in user_region and "whatsapp" in platform:
                conflicts.append("Banned platform in Iran")
                conflict_texts.append("WhatsApp in Iran")
        
        # Check region-specific content
        for region, keywords in PatternLibrary.REGION_CONFLICTS.items():
            if region in user_region:
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        conflicts.append(f"Region-sensitive: {keyword}")
                        conflict_texts.append(keyword)
        
        if conflicts:
            return self._create_flag_result(
                conflicts, conflict_texts, ReasonCode.REGION_VIOLATION, 0.7
            )
        
        return self._create_pass_result(0.85)

# ============================================================================
# MAIN VALIDATION SUITE
# ============================================================================

class AutoValidationSuite:
    """Main validation suite with complete functionality"""
    
    def __init__(self):
        self.validators = [
            EmotionalBaitValidator(),
            SexualEscalationValidator(),
            ManipulativePhrasingValidator(),
            RegionConflictValidator(),
            YouthRiskValidator(),
            LonelinessHookValidator(),
            IllegalIntentValidator()
        ]
        
        # Setup logging
        self._setup_logging()
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "total_validations": 0,
            "blocks": 0,
            "flags": 0,
            "passes": 0,
            "by_category": {cat.value: {"blocks": 0, "flags": 0, "passes": 0} 
                           for cat in RiskCategory},
            "response_times": []
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            handlers=[
                logging.FileHandler(Config.DEBUG_LOG, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def validate(self, content: str, metadata: Optional[Dict] = None) -> ValidationResponse:
        """Main validation method"""
        start_time = datetime.now()
        
        if metadata is None:
            metadata = {}
        
        request_id = str(uuid.uuid4())
        
        # Create request object
        request = ValidationRequest(
            content=content,
            metadata=metadata,
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.logger.info(f"VALIDATION_START | request_id={request_id[:8]} | "
                        f"content_len={len(content)} | region={metadata.get('user_region', 'unknown')}")
        
        results = []
        
        # Run all validators
        for validator in self.validators:
            try:
                result = validator.validate(content, metadata)
                results.append(result)
                
                # Update metrics
                self.metrics["total_validations"] += 1
                category_stats = self.metrics["by_category"][result.risk_category.value]
                
                if result.decision == Decision.BLOCK:
                    category_stats["blocks"] += 1
                    self.metrics["blocks"] += 1
                elif result.decision == Decision.FLAG:
                    category_stats["flags"] += 1
                    self.metrics["flags"] += 1
                else:
                    category_stats["passes"] += 1
                    self.metrics["passes"] += 1
                
                self.logger.info(f"VALIDATOR_RESULT | category={validator.risk_category.value:25} | "
                               f"decision={result.decision.value:6} | "
                               f"confidence={result.confidence:.2f} | "
                               f"patterns={len(result.matched_patterns)}")
                
            except Exception as e:
                self.logger.error(f"VALIDATOR_ERROR | category={validator.risk_category.value} | "
                                f"error={str(e)}")
                
                # Create error result
                results.append(ValidationResult(
                    decision=Decision.FLAG,
                    reason_code=ReasonCode.SYSTEM_ERROR,
                    trace_id=validator.trace_id,
                    risk_category=validator.risk_category,
                    confidence=0.0,
                    matched_patterns=["SYSTEM_ERROR"],
                    matched_text=[f"Error: {str(e)[:50]}"],
                    explanation=f"Validator failed: {str(e)[:100]}"
                ))
        
        # Calculate overall decision
        overall_decision = self._calculate_overall_decision(results)
        
        # Generate summary flag
        summary_flag = self._generate_summary_flag(results, overall_decision)
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        self.metrics["response_times"].append(response_time)
        self.metrics["total_requests"] += 1
        
        # Create response
        response = ValidationResponse(
            request_id=request_id,
            overall_decision=overall_decision,
            summary_flag=summary_flag,
            results=results,
            metrics=self._get_current_metrics(),
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Log completion
        self.logger.info(f"VALIDATION_COMPLETE | request_id={request_id[:8]} | "
                        f"decision={overall_decision.value} | "
                        f"time_ms={response_time:.1f}")
        
        # Save to file
        self._save_validation(request, response)
        
        # Display results
        self._display_results(response)
        
        return response
    
    def _calculate_overall_decision(self, results: List[ValidationResult]) -> Decision:
        """Calculate overall decision with weighted logic"""
        
        # Check for any BLOCK decisions
        block_results = [r for r in results if r.decision == Decision.BLOCK]
        if block_results:
            # Check if any block has critical severity
            critical_blocks = [r for r in block_results if getattr(r, 'severity', 'medium') == 'critical']
            if critical_blocks:
                return Decision.BLOCK
            # Otherwise, use regular block logic
            return Decision.BLOCK
        
        # Check for multiple FLAG decisions
        flag_results = [r for r in results if r.decision == Decision.FLAG]
        if len(flag_results) >= 2:
            # Multiple flags -> escalate to BLOCK
            return Decision.BLOCK
        
        if len(flag_results) == 1:
            # Single flag
            return Decision.FLAG
        
        return Decision.PASS
    
    def _generate_summary_flag(self, results: List[ValidationResult], 
                              overall_decision: Decision) -> str:
        """Generate summary flag"""
        
        if overall_decision == Decision.BLOCK:
            blocking = [r for r in results if r.decision == Decision.BLOCK]
            categories = list(set(r.risk_category.value for r in blocking))
            
            # Check for critical severity
            critical = any(getattr(r, 'severity', 'medium') == 'critical' for r in blocking)
            
            if critical:
                return f"🚨 CRITICAL BLOCK: {categories[0] if categories else 'Multiple violations'}"
            else:
                return f"🛑 BLOCKED: {', '.join(categories[:2])}" if categories else "🛑 BLOCKED"
            
        elif overall_decision == Decision.FLAG:
            flagging = [r for r in results if r.decision == Decision.FLAG]
            categories = list(set(r.risk_category.value for r in flagging))
            return f"⚠️ FLAGGED: {len(categories)} categor{'y' if len(categories) == 1 else 'ies'}"
            
        else:
            return "✅ CLEAN"
    
    def _get_current_metrics(self) -> Dict:
        """Get current metrics"""
        avg_response_time = sum(self.metrics["response_times"][-100:]) / max(len(self.metrics["response_times"][-100:]), 1)
        
        return {
            "total_requests": self.metrics["total_requests"],
            "total_validations": self.metrics["total_validations"],
            "block_rate": self.metrics["blocks"] / max(self.metrics["total_validations"], 1),
            "flag_rate": self.metrics["flags"] / max(self.metrics["total_validations"], 1),
            "pass_rate": self.metrics["passes"] / max(self.metrics["total_validations"], 1),
            "avg_response_time_ms": round(avg_response_time, 1),
            "by_category": self.metrics["by_category"]
        }
    
    def _display_results(self, response: ValidationResponse):
        """Display results to console"""
        print(f"\n{'='*70}")
        print(f"VALIDATION RESULTS - Request: {response.request_id[:8]}")
        print(f"{'='*70}")
        print(f"Overall Decision: {response.overall_decision.value.upper()}")
        print(f"Summary Flag: {response.summary_flag}")
        print(f"Timestamp: {response.timestamp}")
        
        # Show detailed results
        flagged_results = [r for r in response.results if r.decision != Decision.PASS]
        if flagged_results:
            print(f"\n{'─'*70}")
            print("DETAILED RESULTS:")
            print(f"{'─'*70}")
            
            for result in flagged_results:
                print(f"\n[{result.decision.value.upper()}] {result.risk_category.value}:")
                print(f"  Reason: {result.reason_code.value}")
                print(f"  Confidence: {result.confidence:.2f}")
                print(f"  Explanation: {result.explanation}")
                
                if result.matched_text:
                    print(f"  Matched: {', '.join(result.matched_text[:3])}")
                
                print(f"  Trace ID: {result.trace_id}")
    
    def _save_validation(self, request: ValidationRequest, response: ValidationResponse):
        """Save validation to file"""
        try:
            # Read existing data
            try:
                with open(Config.LOG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {"validations": []}
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"validations": [], "metadata": {"version": Config.VERSION}}
            
            # Add new validation
            entry = {
                "request": request.to_dict(),
                "response": response.to_dict(),
                "system": {
                    "version": Config.VERSION,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            data.setdefault("validations", []).append(entry)
            
            # Keep only last 1000 entries
            if len(data["validations"]) > 1000:
                data["validations"] = data["validations"][-1000:]
            
            # Write back
            with open(Config.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save validation: {str(e)}")
    
    def run_test_suite(self):
        """Run comprehensive test suite"""
        print(f"\n{'='*70}")
        print("COMPREHENSIVE TEST SUITE")
        print(f"{'='*70}")
        
        test_cases = [
            {
                "name": "Emotional Dependency Bait",
                "content": "I need you in my life. You're the only one who understands me.",
                "metadata": {"user_region": "us", "platform": "twitter", "user_age": 25},
                "expected": Decision.FLAG
            },
            {
                "name": "Sexual Escalation",
                "content": "Send me nudes and let's meet up alone tonight.",
                "metadata": {"user_region": "eu", "platform": "instagram", "user_age": 17},
                "expected": Decision.BLOCK
            },
            {
                "name": "Violent Threat - Murder",
                "content": "I will kill my sister tomorrow night.",
                "metadata": {"user_region": "us", "platform": "facebook", "user_age": 30},
                "expected": Decision.BLOCK
            },
            {
                "name": "Violent Threat - Bomb",
                "content": "I will bomb this building on Monday.",
                "metadata": {"user_region": "uk", "platform": "twitter", "user_age": 22},
                "expected": Decision.BLOCK
            },
            {
                "name": "Suicide Risk",
                "content": "I want to kill myself, I can't take it anymore.",
                "metadata": {"user_region": "ca", "platform": "reddit", "user_age": 19},
                "expected": Decision.BLOCK
            },
            {
                "name": "Manipulative Phrasing",
                "content": "If you really loved me, you would do this for me.",
                "metadata": {"user_region": "us", "platform": "whatsapp", "user_age": 28},
                "expected": Decision.FLAG
            },
            {
                "name": "Clean Content",
                "content": "Hello! How are you doing today? The weather is nice.",
                "metadata": {"user_region": "au", "platform": "telegram", "user_age": 35},
                "expected": Decision.PASS
            }
        ]
        
        results = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for test in test_cases:
            print(f"\n{'─'*70}")
            print(f"Test: {test['name']}")
            print(f"{'─'*70}")
            print(f"Content: {test['content'][:80]}...")
            
            response = self.validate(test["content"], test["metadata"])
            
            passed = response.overall_decision == test["expected"]
            
            if passed:
                print(f"Result: ✅ PASS (Expected: {test['expected'].value}, Got: {response.overall_decision.value})")
                results["passed"] += 1
            else:
                print(f"Result: ❌ FAIL (Expected: {test['expected'].value}, Got: {response.overall_decision.value})")
                print(f"Summary: {response.summary_flag}")
                results["failed"] += 1
            
            results["details"].append({
                "test": test["name"],
                "expected": test["expected"].value,
                "actual": response.overall_decision.value,
                "passed": passed,
                "summary": response.summary_flag
            })
        
        print(f"\n{'='*70}")
        print("TEST SUITE RESULTS")
        print(f"{'='*70}")
        print(f"Total Tests: {results['total']}")
        print(f"Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
        print(f"Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
        
        if results["failed"] > 0:
            print(f"\nFailed Tests:")
            for detail in results["details"]:
                if not detail["passed"]:
                    print(f"  • {detail['test']}: Expected {detail['expected']}, got {detail['actual']}")
        
        return results

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # ASCII Art Banner
    banner = r"""
     ___      _        _    _       _   _             ___       __        __  
    / _ \    / \      | |  | |     | | | |           / _ \      \ \      / /  
   | | | |  / _ \     | |  | |     | | | |   _____  | | | |_____\ \ /\ / /   
   | |_| | / ___ \    | |__| |     | |_| |  |_____| | |_| |_____ \ V  V /    
    \___/ /_/   \_\    \____/       \___/            \___/       \_/\_/     
                                                                            
    Automated Validation Suite v2.0 | Comprehensive Content Safety System
    """
    
    print(banner)
    print(f"{'='*70}")
    
    # Create validation suite
    suite = AutoValidationSuite()
    
    while True:
        print(f"\n{'='*70}")
        print("MAIN MENU")
        print(f"{'='*70}")
        print("1. Validate custom content")
        print("2. Run comprehensive test suite")
        print("3. View system metrics")
        print("4. Exit")
        print(f"{'='*70}")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print(f"\n{'='*70}")
            print("CUSTOM CONTENT VALIDATION")
            print(f"{'='*70}")
            
            content = input("\nEnter content to validate: ").strip()
            if not content:
                print("❌ Error: Content cannot be empty")
                continue
            
            print("\nOptional metadata (press Enter to skip):")
            user_region = input("User region (e.g., us, eu, china): ").strip()
            platform = input("Platform (e.g., twitter, instagram, facebook): ").strip()
            age_str = input("User age (number): ").strip()
            
            metadata = {}
            if user_region:
                metadata["user_region"] = user_region.lower()
            if platform:
                metadata["platform"] = platform.lower()
            if age_str and age_str.isdigit():
                metadata["user_age"] = int(age_str)
            
            print(f"\n{'─'*40}")
            print("Validating content...")
            print(f"{'─'*40}")
            
            response = suite.validate(content, metadata)
            
            print(f"\n{'='*70}")
            print("VALIDATION COMPLETE")
            print(f"{'='*70}")
            print(f"Request ID: {response.request_id}")
            print(f"Overall Decision: {response.overall_decision.value.upper()}")
            print(f"Summary: {response.summary_flag}")
            
            # Ask if user wants to save to separate file
            save = input("\nSave detailed results to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"validation_{response.request_id[:8]}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(response.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"✅ Results saved to: {filename}")
            
        elif choice == "2":
            print(f"\n{'='*70}")
            print("RUNNING COMPREHENSIVE TEST SUITE")
            print(f"{'='*70}")
            
            results = suite.run_test_suite()
            
            # Ask to save test results
            save = input("\nSave test results to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"✅ Test results saved to: {filename}")
            
        elif choice == "3":
            print(f"\n{'='*70}")
            print("SYSTEM METRICS")
            print(f"{'='*70}")
            
            metrics = suite._get_current_metrics()
            
            print(f"\nOverall Statistics:")
            print(f"  Total Requests: {metrics['total_requests']}")
            print(f"  Total Validations: {metrics['total_validations']}")
            print(f"  Block Rate: {metrics['block_rate']:.2%}")
            print(f"  Flag Rate: {metrics['flag_rate']:.2%}")
            print(f"  Pass Rate: {metrics['pass_rate']:.2%}")
            print(f"  Avg Response Time: {metrics['avg_response_time_ms']:.1f} ms")
            
            print(f"\nCategory Breakdown:")
            for category, stats in metrics['by_category'].items():
                total = stats['blocks'] + stats['flags'] + stats['passes']
                if total > 0:
                    print(f"  {category}:")
                    print(f"    Blocks: {stats['blocks']} ({stats['blocks']/total:.1%})")
                    print(f"    Flags: {stats['flags']} ({stats['flags']/total:.1%})")
                    print(f"    Passes: {stats['passes']} ({stats['passes']/total:.1%})")
            
            print(f"\nLog Files:")
            print(f"  Validation Logs: {Config.LOG_FILE}")
            print(f"  Debug Logs: {Config.DEBUG_LOG}")
            
        elif choice == "4":
            print(f"\n{'='*70}")
            print("Thank you for using the Automated Validation Suite!")
            print("Goodbye! 👋")
            print(f"{'='*70}")
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(Config.SUCCESS)
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        logging.error(f"Critical error in main: {str(e)}", exc_info=True)
        sys.exit(Config.ERROR)
"""
Cycle 5 — No-Go Primitives
==========================

Defines the absolute boundaries of the architecture based on quantum 
information-theoretic limits.

1. No-Cloning: A pure, unknown state cannot be duplicated into an 
   independent, unentangled physical state.
2. No-Deleting: A pure, unknown state cannot be unconditionally destroyed 
   without trace (reversibility of unitary evolution).
3. Confidence Collapse: It is physically impossible to gain classical 
   confidence about a state without forcing a corresponding amount of 
   collapse (measurement disturbance).

These primitives define the Exception structures and type wrappers 
used to architecturally enforce these limits.
"""

class NoGoViolation(Exception):
    """
    Base class for attempts to violate fundamental quantum limits.
    Any operation that triggers this is architecturally falsified.
    """
    pass


class NoCloningViolation(NoGoViolation):
    """
    Raised when an attempt is made to copy a physical state into an 
    independent timeline, branch a state history, or otherwise duplicate 
    quantum information without entanglement.
    """
    def __init__(self, message: str = "Violation of No-Cloning Theorem. Quantum states cannot be duplicated."):
        super().__init__(message)


class NoDeletingViolation(NoGoViolation):
    """
    Raised when an attempt is made to unconditionally destroy a pure state 
    or its history without a valid unitary reverse or measurement collapse.
    """
    def __init__(self, message: str = "Violation of No-Deleting Theorem. Quantum information cannot be erased without trace."):
        super().__init__(message)


class ConfidenceCollapseViolation(NoGoViolation):
    """
    Raised when an operation attempts to acquire classical confidence (knowledge)
    about a state without registering the mandatory measurement disturbance.
    """
    def __init__(self, message: str = "Confidence acquired without registering measurement disturbance. This implies a hidden variable bypass."):
        super().__init__(message)


class StateReference:
    """
    A strong, uncopyable reference to a physical state.
    
    Architectural Enforcement:
    Python allows shallow/deep copying of objects. To enforce No-Cloning 
    architecturally at the integration level, the physical state is wrapped 
    in a StateReference. 
    
    The engine strictly tracks how many active references exist. 
    If a second independent operation tries to evolve a state using a cloned 
    reference, the engine will deterministically fail.
    
    (Note: True linear types don't exist in Python, so we enforce this 
    via registry tracking in the NoGoEnforcementEngine).
    """
    def __init__(self, reference_id: str):
        self.reference_id = reference_id
        
    def __repr__(self) -> str:
        return f"<StateReference id={self.reference_id}>"

    # We cannot strictly prevent deepcopy in all of Python without C-extensions,
    # but we can prevent it at the API layer.
    def __copy__(self):
        raise NoCloningViolation("Attempted to shallow copy a StateReference.")

    def __deepcopy__(self, memo):
        raise NoCloningViolation("Attempted to deep copy a StateReference.")

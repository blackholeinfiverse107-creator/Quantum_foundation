"""
Cycle 9 - Distributed Adversarial Test Runner
================================================

Attempts 5 classes of adversarial attack against the distributed node system:

  1. Conflicting evolution events across nodes
     Two nodes attempt to evolve with different rules simultaneously.
     Expected: both succeed locally but state diverges — divergence is DETECTED,
     not silently accepted. The system surfaces the violation.

  2. Measurement race condition
     Two nodes attempt to measure with the same token_id.
     Expected: second node's token is rejected (token already consumed).

  3. Out-of-order event propagation
     A stale (old logical clock) event is injected after newer events.
     Expected: Lamport clock update absorbs it; idempotency guard drops duplicates.

  4. Duplicate event injection
     The same NetworkEvent is delivered twice to a node.
     Expected: second delivery returns False (silently dropped).

  5. Unregistered rule evolution
     A node attempts to evolve with a rule that was never registered.
     Expected: RuntimeError raised before any state mutation.

Each test records PASS or FAIL with the rejection reason.
"""

from __future__ import annotations

import sys
import os
import json
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cycle9.distributed_state_node import DistributedStateNode, NetworkEvent
from cycle9.node_network_simulation import NodeNetwork, build_standard_network


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _expect_rejection(label: str, fn) -> dict:
    """Run fn(); expect it to raise. Returns result dict."""
    try:
        fn()
        return {"test": label, "status": "FAIL", "reason": "No exception raised — attack was not rejected."}
    except Exception as e:
        return {"test": label, "status": "PASS", "reason": f"Correctly rejected: {type(e).__name__}: {e}"}


def _expect_divergence_detected(label: str, fn) -> dict:
    """Run fn(); expect AssertionError (divergence detected). Returns result dict."""
    try:
        fn()
        return {"test": label, "status": "FAIL", "reason": "No divergence detected — system accepted conflicting state silently."}
    except AssertionError as e:
        return {"test": label, "status": "PASS", "reason": f"Divergence correctly detected: {e}"}
    except Exception as e:
        return {"test": label, "status": "FAIL", "reason": f"Unexpected exception: {type(e).__name__}: {e}"}


def _expect_false(label: str, fn) -> dict:
    """Run fn(); expect it to return False. Returns result dict."""
    try:
        result = fn()
        if result is False:
            return {"test": label, "status": "PASS", "reason": "Duplicate event correctly dropped (returned False)."}
        return {"test": label, "status": "FAIL", "reason": f"Expected False, got {result!r}."}
    except Exception as e:
        return {"test": label, "status": "FAIL", "reason": f"Unexpected exception: {type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Adversarial tests
# ---------------------------------------------------------------------------

def test_conflicting_evolution(results: list) -> None:
    """
    Test 1: Two nodes evolve with different rules without propagating to each other.
    The network bus is NOT used — nodes evolve independently.
    State divergence must be detected when convergence is checked.
    """
    initial = {"0": complex(1.0), "1": complex(0.0)}
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {("0","0"): inv_sq2, ("0","1"): inv_sq2, ("1","0"): inv_sq2, ("1","1"): -inv_sq2}
    x_matrix = {("0","0"): 0.0, ("0","1"): 1.0, ("1","0"): 1.0, ("1","1"): 0.0}

    # Build two isolated nodes (no network bus)
    node_a = DistributedStateNode("NodeA_adv1", initial)
    node_a.observe("H", h_matrix)
    node_a.observe("X", x_matrix)
    node_a.activate()

    node_b = DistributedStateNode("NodeB_adv1", initial)
    node_b.observe("H", h_matrix)
    node_b.observe("X", x_matrix)
    node_b.activate()

    # Wire into a network but evolve with DIFFERENT rules without propagation
    # Simulate by evolving both locally then checking convergence
    network = NodeNetwork()
    network.register_node(node_a)
    network.register_node(node_b)

    # NodeA evolves H (broadcasts to B)
    node_a.evolve("H")
    # Now manually evolve NodeB with X (bypassing the bus — direct harness call)
    # This simulates a conflicting local mutation
    node_b._harness.evolve_deterministic("X")

    def check():
        network.verify_state_convergence()

    results.append(_expect_divergence_detected("T1: Conflicting evolution detected", check))


def test_measurement_race_condition(results: list) -> None:
    """
    Test 2: Two nodes attempt to measure using the same token_id.
    The second measurement must be rejected because the token is already consumed.
    """
    initial = {"0": complex(1.0), "1": complex(0.0)}
    network, node_a, node_b, node_c = build_standard_network(initial)

    # NodeA measures first — this broadcasts to B and C, consuming token "race_token"
    node_a.measure("race_token", seed=42)

    # NodeB now tries to measure with the same token_id
    # receive_event already applied the collapse to B, so its harness already consumed "race_token"
    # Attempting a second direct measure on B with the same token must be rejected
    def attempt():
        node_b.measure("race_token", seed=42)

    results.append(_expect_rejection("T2: Measurement race condition rejected", attempt))


def test_out_of_order_event(results: list) -> None:
    """
    Test 3: A stale event (low logical clock) is injected after newer events.
    The Lamport clock absorbs it. If the event_id was already seen, it is dropped.
    If it is a genuinely new event_id with a stale clock, the clock is updated
    and the event is applied (this is correct Lamport behaviour — ordering is
    enforced by the append-only timeline, not by rejecting stale clocks).
    We verify the timeline remains causally consistent after injection.
    """
    initial = {"0": complex(1.0), "1": complex(0.0)}
    network, node_a, node_b, node_c = build_standard_network(initial)

    # Advance NodeA several steps
    node_a.evolve("H")
    node_a.evolve("X")

    # Construct a stale event with logical_clock=0 (before any real event)
    # Use a new event_id so it is not dropped as duplicate
    stale_event = NetworkEvent(
        event_id="stale_node:0",
        origin_node="stale_node",
        event_type="EVOLUTION",
        logical_clock=0,
        payload=network.global_event_log[0].payload,  # reuse first real payload
    )

    # NodeC receives the stale event — Lamport clock update handles it
    applied = node_c.receive_event(stale_event)

    # Timeline must still be causally consistent
    try:
        node_c._harness.system.timeline.verify_ordering()
        results.append({
            "test": "T3: Out-of-order event absorbed safely",
            "status": "PASS",
            "reason": f"Stale event applied={applied}. Lamport clock updated. Timeline ordering intact."
        })
    except Exception as e:
        results.append({
            "test": "T3: Out-of-order event absorbed safely",
            "status": "FAIL",
            "reason": f"Timeline ordering violated: {e}"
        })


def test_duplicate_event(results: list) -> None:
    """
    Test 4: The same NetworkEvent is delivered twice to a node.
    The second delivery must be silently dropped (returns False).
    """
    initial = {"0": complex(1.0), "1": complex(0.0)}
    network, node_a, node_b, node_c = build_standard_network(initial)

    net_event = node_a.evolve("H")

    # NodeC already received this via the bus. Deliver it again directly.
    def deliver_duplicate():
        return node_c.receive_event(net_event)

    results.append(_expect_false("T4: Duplicate event silently dropped", deliver_duplicate))


def test_unregistered_rule(results: list) -> None:
    """
    Test 5: A node attempts to evolve with a rule that was never registered.
    Must be rejected before any state mutation occurs.
    """
    initial = {"0": complex(1.0), "1": complex(0.0)}
    inv_sq2 = 1.0 / math.sqrt(2)
    h_matrix = {("0","0"): inv_sq2, ("0","1"): inv_sq2, ("1","0"): inv_sq2, ("1","1"): -inv_sq2}

    node = DistributedStateNode("NodeX_adv5", initial)
    node.observe("H", h_matrix)
    node.activate()

    def attempt():
        node.evolve("UNKNOWN_GATE")

    results.append(_expect_rejection("T5: Unregistered rule rejected", attempt))


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(results: list, report_path: str) -> None:
    passed = [r for r in results if r["status"] == "PASS"]
    failed = [r for r in results if r["status"] == "FAIL"]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Distributed Adversarial Test Report\n\n")
        f.write("## Overview\n")
        f.write(
            "This report documents adversarial testing of the distributed quantum node system. "
            "Five attack classes were attempted. Each must be rejected or safely absorbed "
            "without corrupting state, violating causal ordering, or silently accepting invalid input.\n\n"
        )
        f.write(f"## Summary\n")
        f.write(f"- Total tests: `{len(results)}`\n")
        f.write(f"- Passed: `{len(passed)}`\n")
        f.write(f"- Failed: `{len(failed)}`\n")
        f.write(f"- Status: `{'ALL PASS' if not failed else 'FAILURES DETECTED'}`\n\n")
        f.write("## Test Results\n\n")
        for r in results:
            icon = "PASS" if r["status"] == "PASS" else "FAIL"
            f.write(f"### {r['test']}\n")
            f.write(f"- Status: `{icon}`\n")
            f.write(f"- Detail: {r['reason']}\n\n")
        f.write("## Adversarial Classes Covered\n\n")
        f.write("| # | Attack Class | Expected Behaviour | Result |\n")
        f.write("|---|---|---|---|\n")
        rows = [
            ("T1", "Conflicting evolution across nodes", "Divergence detected by convergence check", results[0]["status"]),
            ("T2", "Measurement race condition (same token)", "Second measure rejected — token consumed", results[1]["status"]),
            ("T3", "Out-of-order event propagation", "Lamport clock absorbs; timeline stays consistent", results[2]["status"]),
            ("T4", "Duplicate event injection", "Second delivery dropped (idempotent)", results[3]["status"]),
            ("T5", "Unregistered rule evolution", "Rejected before state mutation", results[4]["status"]),
        ]
        for t, attack, expected, status in rows:
            f.write(f"| {t} | {attack} | {expected} | `{status}` |\n")
        f.write("\n## Conclusion\n")
        if not failed:
            f.write(
                "All adversarial attacks were correctly handled. "
                "The distributed node system enforces determinism, idempotency, "
                "token authority, and causal consistency under adversarial conditions.\n"
            )
        else:
            f.write(f"{len(failed)} test(s) failed. Review required.\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_adversarial_suite() -> str:
    print("Running distributed adversarial test suite...")
    results = []

    test_conflicting_evolution(results)
    test_measurement_race_condition(results)
    test_out_of_order_event(results)
    test_duplicate_event(results)
    test_unregistered_rule(results)

    for r in results:
        icon = "[PASS]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {icon} {r['test']}")

    report_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "distributed_adversarial_report.md")
    )
    write_report(results, report_path)
    print(f"Report -> {report_path}")
    return report_path


if __name__ == "__main__":
    run_adversarial_suite()

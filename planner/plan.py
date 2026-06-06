"""Plan intent — single service dry-run or multi-service STACK."""

from __future__ import annotations

from ir.models import IntentIR
from planner.simulator import DryRunResult, Planner


def plan_intent(ir: IntentIR) -> DryRunResult:
    """Convenience function to plan and simulate an intent."""
    if ir.stack and ir.stack.services:
        from planner.stack_planner import plan_stack

        return plan_stack(ir)
    return Planner().dry_run(ir)

"""
Control Testing Workflow
========================

SequentialAgent
  │
  ├─ 1. control_test_planner   (LlmAgent)   → ControlTestPlan
  │
  ├─ 2. plan_review_loop       (LoopAgent, max_iterations=5)
  │       └─ control_test_reviewer (LlmAgent) → PlanReview  ×4–5
  │
  ├─ 3. control_test_executor  (LlmAgent)   → ControlTestResult
  │       └─ tool: check_user_entitlements(app_name, users)
  │
  └─ 4. control_test_reporter  (LlmAgent)   → ControlTestSummary

The LoopAgent runs the reviewer up to 5 times.  Each iteration covers a
different audit angle (completeness → accuracy → risk → executability → sign-off).
On the 5th iteration the reviewer appends ##ESCALATE## to its feedback, which
is the ADK convention for signalling the LoopAgent to stop early; the loop
also stops automatically at max_iterations=5.
"""
from google.adk.agents import SequentialAgent, LoopAgent

from control_testing.agents.planner_agent import control_test_planner
from control_testing.agents.reviewer_agent import control_test_reviewer
from control_testing.agents.executor_agent import control_test_executor
from control_testing.agents.reporter_agent import control_test_reporter


# --------------------------------------------------------------------------- #
# Review loop — runs the reviewer agent up to 5 times                         #
# --------------------------------------------------------------------------- #
plan_review_loop = LoopAgent(
    name="plan_review_loop",
    description=(
        "Iteratively reviews the ControlTestPlan from 5 different audit angles "
        "(completeness, accuracy, risk, executability, final sign-off). "
        "Stops after 5 iterations or when the reviewer escalates."
    ),
    sub_agents=[control_test_reviewer],
    max_iterations=5,
)


# --------------------------------------------------------------------------- #
# Top-level workflow                                                            #
# --------------------------------------------------------------------------- #
control_testing_workflow = SequentialAgent(
    name="control_testing_workflow",
    description=(
        "End-to-end entitlement control test: plan → multi-pass review "
        "→ execute → summary report."
    ),
    sub_agents=[
        control_test_planner,   # step 1 — produce ControlTestPlan
        plan_review_loop,       # step 2 — 4-5× peer review of the plan
        control_test_executor,  # step 3 — run check_user_entitlements
        control_test_reporter,  # step 4 — write ControlTestSummary
    ],
)

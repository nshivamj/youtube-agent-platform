from google.adk.agents import SequentialAgent, LoopAgent

from agents.control_planner_agent import control_test_planner
from agents.control_reviewer_agent import control_test_reviewer
from agents.control_executor_agent import control_test_executor
from agents.control_reporter_agent import control_test_reporter
from framework.workflow_registry import workflow_registry

# Governance runtime — includes ApprovalCallback + RiskCallback.
# Use this runtime (not the default) when executing this workflow programmatically:
#   from workflows.control_testing_workflow import control_testing_runtime
#   await control_testing_runtime.execute_streaming(control_testing_workflow, ...)
from framework.runtime.agent_runtime import control_testing_runtime  # noqa: F401


# Review loop — runs the reviewer up to 5 times across different audit angles
plan_review_loop = LoopAgent(
    name="plan_review_loop",
    description=(
        "Iteratively reviews the ControlTestPlan from 5 audit angles: "
        "completeness, accuracy, risk coverage, executability, final sign-off."
    ),
    sub_agents=[control_test_reviewer],
    max_iterations=5,
)

# End-to-end workflow: plan → review (×5) → execute → report
control_testing_workflow = SequentialAgent(
    name="control_testing_workflow",
    description=(
        "Entitlement control test: plan → multi-pass peer review "
        "→ execute check_user_entitlements → ControlTestSummary report."
    ),
    sub_agents=[
        control_test_planner,   # step 1 — produce ControlTestPlan
        plan_review_loop,       # step 2 — 5× peer review
        control_test_executor,  # step 3 — run check_user_entitlements
        control_test_reporter,  # step 4 — write ControlTestSummary
    ],
)

workflow_registry.register(
    name="control_testing_workflow",
    workflow=control_testing_workflow,
    description=(
        "Runs an end-to-end entitlement control test: plan, peer review, "
        "execute access checks, and produce a compliance summary report"
    ),
    triggers=[
        "run control test",
        "check entitlements",
        "audit user access",
        "test who has access to",
        "compliance check",
    ],
)

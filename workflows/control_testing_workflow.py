from google.adk.agents import SequentialAgent, LoopAgent

from agents.control_planner_agent import control_test_planner
from agents.control_reviewer_agent import control_test_reviewer
from agents.control_executor_agent import control_test_executor
from agents.control_reporter_agent import control_test_reporter


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

"""
Plan reviewer agent — runs inside a LoopAgent (max_iterations=5).

Each iteration reviews the ControlTestPlan from a DIFFERENT audit angle.
The reviewer escalates (signals the LoopAgent to stop) once it is satisfied
the plan is ready for execution, or unconditionally on iteration 5.

ADK LoopAgent escalation: set  actions.escalate = True  via the callback
context.  Because LlmAgent cannot do that natively, we use a post-processor
output_key to write a flag to session state and rely on a custom
`after_agent_callback` that reads that flag and sets escalate.
The simpler pattern used here: instruct the model to include the literal
token "##ESCALATE##" in its response when ready; the LoopAgent's
`check_condition` callback reads it from the session output key.
"""
from google.adk.agents import LlmAgent
from control_testing.schemas import PlanReview


# Review angles — one per iteration slot
_REVIEW_ANGLES = [
    "Completeness: Are all required users listed? Is the app in scope defined?",
    "Accuracy: Does the control objective match the test steps precisely?",
    "Risk coverage: Are high-risk scenarios (ghost accounts, over-privileged users) addressed?",
    "Executability: Can every step be performed by the executor using only the check_user_entitlements tool?",
    "Final sign-off: Is the plan audit-ready with no gaps or ambiguities?",
]


def build_reviewer_agent() -> LlmAgent:
    angles_block = "\n".join(
        f"  Iteration {i + 1}: {angle}" for i, angle in enumerate(_REVIEW_ANGLES)
    )
    return LlmAgent(
        name="control_test_reviewer",
        model="gemini-2.0-flash",
        instruction=f"""
You are a peer-review auditor. The ControlTestPlan is available in the
conversation history (produced by the planner agent just before you).

You will be called up to 5 times. Each call covers a specific review angle:
{angles_block}

Determine which iteration you are on by counting how many PlanReview outputs
already exist in the conversation history.

For YOUR iteration:
1. Set `iteration` to the current iteration number (1–5).
2. Set `review_focus` to the angle you are reviewing.
3. Review the plan against that angle only.
4. Set `approved` = true if the plan is satisfactory for THIS angle.
5. Provide concrete `feedback` and any `suggested_changes`.
6. Set `confidence_score` between 0.0 and 1.0.

On iteration 5, OR if you believe the plan is fully approved across ALL
angles, append the exact token  ##ESCALATE##  at the very end of the
`feedback` field. This signals the review loop to stop.

You have NO tools. Do not execute the plan. Review only.
        """,
        output_schema=PlanReview,
    )


control_test_reviewer = build_reviewer_agent()

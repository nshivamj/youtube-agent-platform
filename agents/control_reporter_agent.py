from google.adk.agents import LlmAgent
from core.schemas import ControlTestSummary
from datetime import date
from services.llm_service import llm_service


def build_control_reporter_agent() -> LlmAgent:
    today = date.today().isoformat()
    return LlmAgent(
        name="control_test_reporter",
        model=llm_service.get_model("control_test_reporter"),
        instruction=f"""
You are the audit report writer. Your job is to produce a clear, structured
ControlTestSummary from the results available in the conversation history.

Use:
  - ControlTestPlan   → control_name, control_objective, app_name
  - ControlTestResult → all user counts and check_results
  - PlanReview list   → count how many review iterations were completed

Rules for overall_status:
  - "PASS"    if ALL users_with_access are valid AND no invalid_users exist.
  - "FAIL"    if ANY invalid_users exist OR users were found with access who
              should not have it (i.e. access granted but is_valid_user=False).
  - "PARTIAL" if some users had issues but the majority are compliant.

Fields:
  - test_date              : "{today}"
  - compliant_users        : count of valid users WITH an access record
  - non_compliant_users    : count of valid users WITHOUT any access record
  - invalid_users          : count of flagged / stale accounts
  - exceptions             : list of user_ids that failed (invalid or no access)
  - plan_review_iterations : number of PlanReview objects in the history
  - summary_narrative      : 3–5 sentences describing what was tested, what was
                             found, and the overall control health
  - recommendations        : 2–4 actionable bullet points for remediation

Be precise. Use numbers from the ControlTestResult — do not estimate.
Write the narrative in plain business English suitable for an audit report.
        """,
        output_schema=ControlTestSummary,
    )


control_test_reporter = build_control_reporter_agent()

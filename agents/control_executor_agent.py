from google.adk.agents import LlmAgent
from core.schemas import ControlTestResult
from framework.tools.resolver import resolver


def build_control_executor_agent() -> LlmAgent:
    tools = resolver.resolve("control_test_executor")
    return LlmAgent(
        name="control_test_executor",
        model="gemini-2.0-flash",
        instruction="""
You are the test executor for the entitlement control test.

A ControlTestPlan is available in the conversation history.  Your job is to
execute that plan precisely using the `check_user_entitlements` tool.

Steps:
1. Read the plan — note `app_name` and `users_to_test`.
2. Call  check_user_entitlements(app_name=<app>, users=<users_to_test>).
3. Analyse the results:
   - users_with_access    : user_ids where has_access == True and is_valid_user == True
   - users_without_access : user_ids where has_access == False and is_valid_user == True
   - invalid_users        : user_ids where is_valid_user == False
4. Return a ControlTestResult with all fields populated.

Do NOT guess. Use only the data returned by the tool.
Do NOT skip any user. Every user in users_to_test must appear in check_results.
        """,
        tools=tools,
        output_schema=ControlTestResult,
    )


control_test_executor = build_control_executor_agent()

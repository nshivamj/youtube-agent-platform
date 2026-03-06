import inspect
from framework.tools.registry import registry


# Methods to expose per domain — keeps tool surface area intentional
DOMAIN_METHODS = {
    "youtube": [
        "get_watch_summary",
        "get_shorts_ratio",
        "get_top_channels",
        "get_watch_by_hour",
        "get_binge_sessions",
    ],
    "file": [
        "save_report",
        "list_reports",
        "get_report",
    ],
    "entitlement": [
        "check_user_entitlements",
    ],
}


class ToolResolver:
    """Selects which tools an agent gets based on agent role + environment.
    Extracts individual async methods from tool instances and returns them
    as plain callables that ADK can use as FunctionTools."""

    AGENT_DOMAINS = {
        "analyzer_agent": ["youtube"],
        "insights_agent": ["file"],
        "coordinator_agent": [],
        "planner_agent": [],
        # Control testing agents
        "control_test_planner": [],
        "control_test_reviewer": [],
        "control_test_executor": ["entitlement"],
        "control_test_reporter": [],
    }

    def resolve(self, agent_name: str) -> list:
        domains = self.AGENT_DOMAINS.get(agent_name, [])
        tools = []
        for domain in domains:
            tool_instance = registry.get(domain)
            if not tool_instance:
                continue
            for method_name in DOMAIN_METHODS.get(domain, []):
                method = getattr(tool_instance, method_name, None)
                if method and callable(method):
                    tools.append(method)
        return tools


resolver = ToolResolver()

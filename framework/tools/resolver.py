from framework.tools.registry import registry


# Methods to expose per domain — keeps tool surface area intentional.
# When you add a new domain tool, add its exposed methods here.
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

    Agents self-declare their domains by calling resolver.declare() in their
    own module — no manual edits to this file needed when adding new agents.

    Extracts individual async methods from tool instances and returns them
    as plain callables that ADK can use as FunctionTools.
    """

    def __init__(self):
        self._agent_domains: dict[str, list[str]] = {}

    def declare(self, agent_name: str, domains: list[str]):
        """Called by each agent module to register which tool domains it needs.

        Example (in agents/my_agent.py):
            resolver.declare("my_agent", domains=["youtube", "file"])
        """
        self._agent_domains[agent_name] = domains

    def resolve(self, agent_name: str) -> list:
        domains = self._agent_domains.get(agent_name, [])
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

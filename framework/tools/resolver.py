class ToolResolver:
    """Flat name → callable tool registry.

    Two responsibilities:
    - register_tool(name, fn): called once at startup by ToolRegistry for every
      active tool method (respects TOOL_MODE local/mcp swap automatically).
    - declare(agent_name, tools=[...]): called by each agent to list exactly
      which tool names it needs — no bundles, no domain indirection.
    - resolve(agent_name): returns the callables that agent declared.

    Adding a new agent: call resolver.declare() in the agent file — done.
    Adding a new tool:  add the method to the tool class + tool_names — done.
    No central config to edit in either case.
    """

    def __init__(self):
        self._tools: dict[str, callable] = {}
        self._agent_tools: dict[str, list[str]] = {}

    def register_tool(self, name: str, fn: callable):
        """Called by ToolRegistry to expose a tool callable by name."""
        self._tools[name] = fn

    def declare(self, agent_name: str, tools: list[str]):
        """Called by each agent module to declare its exact tool surface.

        Example (in agents/my_agent.py):
            resolver.declare("my_agent", tools=["get_watch_summary", "save_report"])
        """
        self._agent_tools[agent_name] = tools

    def resolve(self, agent_name: str) -> list:
        return [
            self._tools[t]
            for t in self._agent_tools.get(agent_name, [])
            if t in self._tools
        ]


resolver = ToolResolver()

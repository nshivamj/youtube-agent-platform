class ToolResolver:
    """Flat name → callable tool registry.

    Three responsibilities:
    - register_tool(name, fn): called once at startup by ToolRegistry for every
      active tool method (respects TOOL_MODE local/mcp swap automatically).
    - register_agent_tool(name, agent_tool): called to register an ADK AgentTool
      wrapping a sub-agent so it can be declared by name like any other tool.
    - declare(agent_name, tools=[...]): called by each agent to list exactly
      which tool names it needs — no bundles, no domain indirection.
    - resolve(agent_name): returns the callables/AgentTools that agent declared.

    Adding a new agent:       call resolver.declare() in the agent file — done.
    Adding a new tool:        add the method to the tool class + tool_names — done.
    Adding agent-to-agent:    resolver.register_agent_tool("name", AgentTool(agent=x))
                              then declare it like any other tool — done.
    No central config to edit in any case.
    """

    def __init__(self):
        self._tools: dict[str, callable] = {}
        self._agent_tools: dict[str, list[str]] = {}

    def register_tool(self, name: str, fn: callable):
        """Called by ToolRegistry to expose a tool callable by name."""
        self._tools[name] = fn

    def register_agent_tool(self, name: str, agent_tool):
        """Register an ADK AgentTool so it can be declared by name.

        This is the agent-to-agent bridge. Any agent that needs to call another
        agent as a sub-agent declares the name here and resolves it like any
        other tool.

        Usage (in the parent agent's module or an init file):
            from google.adk.tools import AgentTool
            from agents.analyzer_agent import analyzer_agent
            resolver.register_agent_tool("call_analyzer", AgentTool(agent=analyzer_agent))

        Then in the parent agent:
            resolver.declare("coordinator_agent", tools=["call_analyzer"])
        """
        self._tools[name] = agent_tool

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

"""Single import that registers every tool.

Import this module once (factory.py does it) and all @tool-decorated functions
land in framework.tools.registry._registry, ready for get_many().

To add a new tool module: create tools/local/my_tools.py with @tool functions,
then add one import line here.
"""
import tools.local.gitlab_tools       # noqa: F401
import tools.local.youtube_tools      # noqa: F401
import tools.local.file_tools         # noqa: F401
import tools.local.entitlement_tools  # noqa: F401

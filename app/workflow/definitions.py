"""Workflow data definitions.

A WorkflowDefinition is a named sequence of WorkflowSteps.
Each step specifies which agent to run and a prompt template.

Template variables available in prompt_template:
    {input}           — the original user prompt passed to the workflow
    {previous_output} — the text output of the immediately preceding step
"""

from dataclasses import dataclass, field


@dataclass
class WorkflowStep:
    agent: str
    prompt_template: str


@dataclass
class WorkflowDefinition:
    name: str
    description: str
    steps: list[WorkflowStep] = field(default_factory=list)

# Copyright (c) Microsoft. All rights reserved.

"""Task management agent with human-in-the-loop capabilities."""

from typing import Literal
from pydantic import BaseModel, Field
from agent_framework import ChatAgent, ChatClientProtocol, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent, TaskPlannerConfirmationStrategy


class TaskStep(BaseModel):
    """A single task step."""
    description: str = Field(description="Brief description of the step")
    status: Literal["enabled", "disabled", "executing"] = Field(
        default="enabled",
        description="Status of the step"
    )


@ai_function(
    name="generate_task_plan",
    description="Generate a step-by-step task plan",
    approval_mode="always_require"
)
def generate_task_plan(
    task_description: str,
    steps: list[TaskStep]
) -> str:
    """Generate execution steps for a task.

    Args:
        task_description: Description of the task to plan
        steps: List of steps to complete the task (typically 5-10 steps)

    Returns:
        Confirmation message
    """
    return f"Generated {len(steps)} steps for: {task_description}"


@ai_function(
    name="execute_task_steps",
    description="Execute the approved task steps"
)
def execute_task_steps(steps: list[str]) -> str:
    """Execute a list of task steps.
    
    Args:
        steps: List of step descriptions to execute
        
    Returns:
        Execution result message
    """
    return f"Successfully executed {len(steps)} steps:\n" + "\n".join(f"✓ {step}" for step in steps)


def task_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a task management agent with human-in-the-loop.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance with task planning
    """
    agent = ChatAgent(
        name="task_planning_agent",
        instructions="""You are an expert task planner and executor.
        
        Your role:
        - Break down complex tasks into clear, actionable steps
        - Create step-by-step plans that users can review and approve
        - Execute approved tasks efficiently
        
        When planning tasks:
        1. Analyze the user's request carefully
        2. Create 5-10 clear, concise steps
        3. Each step should be specific and actionable
        4. Use imperative language (e.g., "Research options", "Create document")
        5. Present the plan to the user for approval
        
        After approval:
        - Execute the approved steps
        - Provide progress updates
        - Confirm completion
        
        Be thorough but concise. Focus on practical, achievable steps.
        """,
        chat_client=chat_client,
        tools=[generate_task_plan, execute_task_steps],
        streaming=True, # Enable streaming responses can be disabled if not needed
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="TaskPlanner",
        description="Plans and executes tasks with human oversight",
        confirmation_strategy=TaskPlannerConfirmationStrategy(),
        require_confirmation=True,
    )

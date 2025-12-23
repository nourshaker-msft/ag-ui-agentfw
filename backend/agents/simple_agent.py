# Copyright (c) Microsoft. All rights reserved.

"""Simple chat agent for basic conversations."""

from agent_framework import ChatAgent, ChatClientProtocol
from agent_framework.ag_ui import AgentFrameworkAgent


def simple_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a simple chat agent.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance
    """
    agent = ChatAgent(
        name="simple_chat_agent",
        instructions="""You are a helpful and friendly AI assistant. 
        
        Your role:
        - Provide clear, concise, and accurate responses
        - Be conversational and engaging
        - Help users with a wide variety of tasks
        - If you don't know something, admit it honestly
        
        Communication style:
        - Be warm and approachable
        - Use simple language when possible
        - Provide examples when helpful
        - Break down complex topics into digestible pieces
        """,
        chat_client=chat_client,
        temperature=0.5,
        top_p=0.5
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="SimpleChat",
        description="A helpful AI assistant for general conversations",
    )

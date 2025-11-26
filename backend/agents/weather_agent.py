# Copyright (c) Microsoft. All rights reserved.

"""Weather agent with tool rendering capabilities."""

from agent_framework import ChatAgent, ChatClientProtocol, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent


@ai_function
def get_weather(location: str) -> dict:
    """Get weather information for a location.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        Weather information including temperature, conditions, humidity, wind speed, and feels like
    """
    # Mock weather data - in production, this would call a real weather API
    import random
    
    conditions = ["sunny", "cloudy", "partly cloudy", "rainy", "clear"]
    
    base_temp = random.randint(15, 30)
    
    return {
        "location": location,
        "temperature": base_temp,
        "conditions": random.choice(conditions),
        "humidity": random.randint(40, 80),
        "wind_speed": random.randint(5, 25),
        "feels_like": base_temp + random.randint(-3, 3)
    }


def weather_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a weather agent with tool rendering.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance with weather tools
    """
    agent = ChatAgent(
        name="weather_agent",
        instructions="""You are a weather information assistant.
        
        Your capabilities:
        - Retrieve current weather information for any location
        - Provide weather details including temperature, conditions, humidity, and wind
        - Give helpful advice based on weather conditions
        
        When a user asks about weather:
        1. Use the get_weather tool to fetch current data
        2. Present the information in a friendly, conversational way
        3. Offer relevant suggestions (e.g., "It's sunny, great day for a walk!")
        
        Always be enthusiastic about sharing weather information!
        """,
        chat_client=chat_client,
        tools=[get_weather],
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="WeatherAgent",
        description="Get weather information with beautiful UI rendering",
    )

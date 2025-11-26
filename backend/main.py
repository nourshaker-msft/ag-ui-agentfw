# Copyright (c) Microsoft. All rights reserved.

"""FastAPI server with AG-UI integration for weather and task management agents."""

import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework.azure import AzureOpenAIChatClient

from agents.weather_agent import weather_agent
from agents.task_agent import task_agent
from agents.simple_agent import simple_agent
from agents.recipe_agent import recipe_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent Framework + CopilotKit Demo",
    description="Full-stack agentic chat application with AG-UI + Microsoft Agent Framework + CopilotKit",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Azure OpenAI chat client
logger.info("Using Azure OpenAI chat client")
chat_client = AzureOpenAIChatClient(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
)

# Add agent endpoints
logger.info("Setting up agent endpoints...")

# Simple chat agent
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=simple_agent(chat_client),
    path="/simple",
)
logger.info("✓ Simple chat agent endpoint: /simple")

# Weather agent with tool rendering
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=weather_agent(chat_client),
    path="/weather",
)
logger.info("✓ Weather agent endpoint: /weather")

# Task management agent with human-in-the-loop
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=task_agent(chat_client),
    path="/tasks",
)
logger.info("✓ Task agent endpoint: /tasks")

# Recipe agent with shared state
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=recipe_agent(chat_client),
    path="/shared_state",
)
logger.info("✓ Recipe agent endpoint: /shared_state")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Agent Framework + CopilotKit Demo API",
        "version": "1.0.0",
        "endpoints": {
            "/simple": "Simple chat agent",
            "/weather": "Weather agent with tool rendering",
            "/tasks": "Task management agent with human-in-the-loop",
            "/shared_state": "Recipe agent with shared state management",
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    """Run the server."""
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on http://localhost:{port}")
    logger.info("API documentation available at http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

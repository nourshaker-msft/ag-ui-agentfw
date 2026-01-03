# Copyright (c) Microsoft. All rights reserved.

"""FastAPI server with AG-UI integration for weather and task management agents."""

import logging
import os
from dotenv import load_dotenv

load_dotenv()

import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agent_framework.ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework.azure import AzureOpenAIChatClient, AzureOpenAIResponsesClient, AzureAIClient

from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient

# Apply patch for azure-core to fix brotli decompression issue
try:
    from patch_azure_core import apply_patch as apply_azure_core_patch
    apply_azure_core_patch()
except ImportError as e:
    logging.warning(f"Could not import patch_azure_core: {e}. Brotli decompression might fail.")

# Apply patch for OpenAI responses client to fix payload format for Azure AI
try:
    from patch_openai_responses import apply_patch as apply_openai_responses_patch
    apply_openai_responses_patch()
except ImportError as e:
    logging.warning(f"Could not import patch_openai_responses: {e}. Azure AI requests might fail.")

# Apply patch for AG-UI event bridge to fix tool call streaming issue
try:
    from patch_agent_framework import apply_patch
    apply_patch()
except ImportError as e:
    logging.warning(f"Could not import patch_agent_framework: {e}. Tool call streaming might be broken.")

from azure.identity import DefaultAzureCredential

from agents.weather_agent import weather_agent
from agents.task_agent import task_agent
from agents.simple_agent import simple_agent
from agents.recipe_agent import recipe_agent
from agents.file_search_agent import file_search_agent, upload_file_to_azure_ai
from agents.image_agent import image_agent

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agent Framework + CopilotKit Demo",
    description="Full-stack agentic chat application with AG-UI + Microsoft Agent Framework + CopilotKit",
    version="1.0.0",
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

credential = DefaultAzureCredential()

###### Initialize Azure OpenAI chat client ######
# chat_client = AzureOpenAIChatClient(
#     endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     credential=credential,
#     deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
# )  

###### Initialize Azure OpenAI responses client with streaming ######
# chat_client = AzureOpenAIResponsesClient(
#     endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     credential=credential,
#     deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
#     streaming=True,
# )

# Initialize Azure AI client with conversation
convo_id=AIProjectClient(
            endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            credential=credential,
        ).get_openai_client().conversations.create().id

chat_client = AzureAIClient(
    project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
    credential=credential,
    conversation_id=convo_id,
    model_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
    agent_name="ag-ui-fastapi-server",
    streaming=True,
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

# Image generation agent
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=image_agent(chat_client),
    path="/image",
)
logger.info("✓ Image agent endpoint: /image")


# File search agent with Azure AI
# Note: This must be recreated on each upload to properly sync tool configuration
def create_file_search_agent():
    """Factory function to create a new file search agent instance."""
    return file_search_agent(chat_client)

# Will be initialized on startup
file_search_agent_instance = None

@app.on_event("startup")
async def startup_event():
    """Initialize agents that require async setup."""
    global file_search_agent_instance
    file_search_agent_instance = create_file_search_agent()
    
    add_agent_framework_fastapi_endpoint(
        app=app,
        agent=file_search_agent_instance,
        path="/file-search",
    )
    logger.info("✓ File search agent endpoint: /file-search")


@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file for the file search agent.
    
    Args:
        file: The uploaded file
        
    Returns:
        Upload status and file information
    """
    try:
        # Create a temporary file to save the upload
        with tempfile.NamedTemporaryFile(delete=False, 
                                         prefix=Path(file.filename or "file").stem, 
                                         suffix=Path(file.filename or "file").suffix) as temp_file:
            # Read and write the file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Get the file search agent to access project client and vector store
        agent = file_search_agent_instance
        
        if not hasattr(agent, '_project_client') or not agent._project_client:
            # Clean up temp file
            Path(temp_file_path).unlink(missing_ok=True)
            raise HTTPException(
                status_code=503,
                detail="Azure AI Project client not configured. Please set AZURE_AI_PROJECT_ENDPOINT environment variable."
            )
        
        # Track if this is the first file upload
        is_first_upload = not agent._vector_store_id
        
        # Upload to Azure AI and get updated vector store ID
        result, new_vector_store_id = await upload_file_to_azure_ai(
            agents_client=agent._project_client,
            vector_store_id=agent._vector_store_id,
            file_path=temp_file_path,
            filename=file.filename or "unknown",
        )
        
        # Update the vector store ID and agent tools if it was created for the first time
        if new_vector_store_id and not agent._vector_store_id:
            agent._vector_store_id = new_vector_store_id
            
            # IMPORTANT: Update the agent's tools to include file search
            # This prevents KeyError in conversation history
            from agent_framework import HostedFileSearchTool
            
            # Recreate the agent with the new tool to avoid conversation history issues
            # The AG-UI framework maintains conversation history which causes KeyError
            # when tool configurations change mid-conversation
            logger.info(f"Vector store created: {new_vector_store_id}. Agent will use file search on next request.")
            
            # Add the file search tool to the underlying agent
            if hasattr(agent, '_agent') and agent._agent:
                # Clear any existing file search tools first
                agent._agent.tools = [t for t in agent._agent.tools if not isinstance(t, HostedFileSearchTool)]
                # Add the new tool
                new_tool = HostedFileSearchTool(inputs=new_vector_store_id)
                agent._agent.tools.append(new_tool)
                logger.info(f"Added HostedFileSearchTool to agent with vector store {new_vector_store_id}")
        
        # Clean up temp file
        Path(temp_file_path).unlink(missing_ok=True)
        
        if result.status == "success":
            response = {
                "status": "success",
                "message": result.message,
                "filename": result.filename,
                "file_id": result.file_id,
            }
            
            # Add a special message if this was the first upload
            if is_first_upload:
                response["message"] = f"{result.message}. Please start a new conversation to use file search."
                response["requires_refresh"] = True
            
            return response
        else:
            raise HTTPException(status_code=500, detail=result.message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


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
            "/file-search": "Document search agent with Azure AI file search",
            "/image": "Image generation agent",
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

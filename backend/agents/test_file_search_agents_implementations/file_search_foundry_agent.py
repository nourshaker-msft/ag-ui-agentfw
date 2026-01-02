# Copyright (c) Microsoft. All rights reserved.

"""File search agent using Azure AI Agent with file upload and search capabilities."""

import os
import logging
import random
from typing import Optional
from azure.ai.projects import AIProjectClient
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FileInfo, VectorStore
from azure.identity import DefaultAzureCredential

from agent_framework import ChatAgent, HostedFileSearchTool, HostedVectorStoreContent
from agent_framework.azure import AzureOpenAIChatClient, AzureAIClient, AzureOpenAIResponsesClient
from agent_framework.ag_ui import AgentFrameworkAgent
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class FileSearchResult(BaseModel):
    """Result of a file search query."""

    query: str = Field(..., description="The search query")
    results: str = Field(..., description="Search results from uploaded files")
    sources: list[str] = Field(
        default_factory=list, description="Source files referenced"
    )


class FileUploadStatus(BaseModel):
    """Status of a file upload operation."""

    filename: str = Field(..., description="Name of the uploaded file")
    status: str = Field(..., description="Upload status (success/error)")
    message: str = Field(default="", description="Status message")
    file_id: Optional[str] = Field(None, description="Azure AI file ID if successful")


_FILE_SEARCH_INSTRUCTIONS = """You are a helpful file search assistant powered by Azure AI.

Your capabilities:
1. Help users search through uploaded documents
2. Answer questions based on the content of uploaded files
3. Provide accurate information with source citations

When a user asks a question:
- If files have been uploaded, search through them to find relevant information
- Provide clear, accurate answers based on the file contents
- Cite the source files when referencing information
- If information is not found in the files, clearly state that
- If no files have been uploaded yet, politely let the user know they need to upload documents first

Be helpful, accurate, and always reference your sources!
"""


def file_search_agent(chat_client: AzureOpenAIChatClient) -> AgentFrameworkAgent:
    """Create a file search agent with Azure AI file search capabilities.

    This agent allows users to upload files and search through them using
    Azure AI's vector search capabilities.

    Args:
        chat_client: The chat client to use for the agent

    Returns:
        A configured AgentFrameworkAgent instance with file search capabilities
    """
    # Get Azure AI Project configuration from environment
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    
    if not project_endpoint:
        logger.warning(
            "AZURE_AI_PROJECT_ENDPOINT not set. "
            "File search agent will have limited functionality."
        )

    # Initialize Azure AI agents client
    agents_client = None
    credential = DefaultAzureCredential()
    
    if project_endpoint:
        try:
            # Create async agents client
            agents_client = AgentsClient(
                endpoint=project_endpoint,
                credential=credential,
            )
            logger.warning(f"Initialized Azure AI agents client with endpoint: {project_endpoint}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI agents client: {e}", exc_info=True)
            agents_client = None

    # Create the chat agent WITHOUT file search tool initially
    # The tool will be added dynamically when files are uploaded
    # This avoids initialization issues with async vector store creation
    tools = []
    vector_store_id = None

    if agents_client:
        vector_store_id = agents_client.vector_stores.create_and_poll(
            name=f"FileSearchVectorStore_{random.randint(1000, 9999)}",
            file_ids=[]).id
        print(f"Created vector store with ID: {vector_store_id}")
    
    # agent = ChatAgent(
    #     name="file_search_agent",
    #     instructions=_FILE_SEARCH_INSTRUCTIONS,
    #     chat_client=chat_client,
    #     tools=tools,
    #     streaming=True,
    # )

    ai_client = AzureAIClient(
        agent_name="file-search-agent",
        project_endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
        model_deployment_name="gpt-4.1",
        streaming=True,
        )
    
    file_search_tool = HostedFileSearchTool(inputs=[HostedVectorStoreContent(vector_store_id=vector_store_id)])
    
    ai_client.create_agent(
        tools=file_search_tool
    )

    convo_id=AIProjectClient(
            endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            credential=credential,
        ).get_openai_client().conversations.create().id
    
    agent = ChatAgent(
        chat_client=ai_client,
        name = "file_search_agentfw",
        instructions=_FILE_SEARCH_INSTRUCTIONS,
        tools=file_search_tool,
        conversation_id=convo_id,
        )

    # Create the agent framework wrapper
    ag_agent = AgentFrameworkAgent(
        agent=agent,
        name="FileSearchAgent",
        description="Search and analyze uploaded documents using Azure AI",
        state_schema={
            "uploaded_files": {
                "type": "array",
                "description": "List of uploaded files",
                "items": {"type": "object"},
            },
            "search_results": {
                "type": "object",
                "description": "Latest search results",
            },
        },
    )
    
    # Store references for file operations
    ag_agent._project_client = agents_client  # type: ignore
    ag_agent._vector_store_id = vector_store_id  # type: ignore
    ag_agent._project_endpoint = project_endpoint  # type: ignore

    return ag_agent


async def upload_file_to_azure_ai(
    agents_client: AzureOpenAIChatClient,
    vector_store_id: Optional[str],
    file_path: str,
    filename: str,
) -> tuple[FileUploadStatus, Optional[str]]:
    """Upload a file to Azure AI and add it to the vector store.

    Args:
        agents_client: The Azure AI agents client
        vector_store_id: ID of the vector store (or None to create one)
        file_path: Path to the file to upload
        filename: Original filename

    Returns:
        Tuple of (FileUploadStatus, vector_store_id)
    """
    try:
        # Upload the file
        file = agents_client.files.upload(
            file_path=file_path,
            purpose="assistants",
        )
        logger.warning(f"Uploaded file {filename} with ID {file.id}")
        
        # Create vector store if it doesn't exist
        if vector_store_id is None:
            vector_store = agents_client.vector_stores.create_and_poll(
                name=f"FileSearchVectorStore_{random.randint(1000, 9999)}",
                file_ids=[]
            )
            vector_store_id = vector_store.id
            logger.warning(f"Created new vector store with ID {vector_store_id}")
        
        # Add file to existing vector store
        agents_client.vector_store_files.create(
            vector_store_id=vector_store_id,
            file_id=file.id,
        )
        logger.warning(f"Added file {file.id} to vector store {vector_store_id}")
        
        return (
            FileUploadStatus(
                filename=filename,
                status="success",
                message=f"File '{filename}' uploaded successfully",
                file_id=file.id,
            ),
            vector_store_id,
        )
        
    except Exception as e:
        logger.error(f"Failed to upload file {filename}: {e}", exc_info=True)
        return (
            FileUploadStatus(
                filename=filename,
                status="error",
                message=f"Failed to upload file: {str(e)}",
            ),
            vector_store_id,
        )

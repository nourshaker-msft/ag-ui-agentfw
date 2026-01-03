# Copyright (c) Microsoft. All rights reserved.

"""Image generation agent."""

import os
import logging
import base64
from typing import Callable, Awaitable
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, ImageGenTool
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from agent_framework import ChatAgent, ChatClientProtocol, DataContent, TextContent, ai_function, FunctionCallContent
from agent_framework.ag_ui import AgentFrameworkAgent
from agent_framework.azure import AzureAIClient
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)

# Configuration
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
IMAGE_AGENT_NAME = "ag-ui-image-gen-agent"
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")

IMAGE_GEN_MODEL = "gpt-image-1.5"  # currently only support gpt-image-1 and gpt-image-1.5
IMAGE_GEN_HEADERS = {"x-ms-oai-image-generation-deployment": IMAGE_GEN_MODEL}

class ImageState(BaseModel):
    """State for the generated image."""
    url: str = Field(description="URL or data URI of the generated image")
    prompt: str = Field(description="The prompt used to generate the image")

@ai_function
def update_image(image: ImageState) -> str:
    """Update the image state with a newly generated image.
    
    This function is called automatically when an image is generated.
    The image URL can be a standard URL or a data URI (data:image/png;base64,...).
    
    Args:
        image: The image state containing URL and prompt
        
    Returns:
        Confirmation message
    """
    return f"Image updated with prompt: {image.prompt}"

class ImageGenChatAgent(ChatAgent):
    """Custom ChatAgent Class that automatically adds image generation headers and extracts images to state."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_user_prompt = None
        self._processed_image_ids = set()
    
    ### Override run_stream to inject headers and handle image content
    async def run_stream(self, *args, **kwargs):
        # Inject headers into additional_chat_options
        additional_chat_options = kwargs.get("additional_chat_options", {})
        extra_headers = additional_chat_options.get("extra_headers", {})
        
        # Update with image gen headers
        if isinstance(extra_headers, dict):
            extra_headers.update(IMAGE_GEN_HEADERS)
        else:
            extra_headers = IMAGE_GEN_HEADERS.copy()
            
        additional_chat_options["extra_headers"] = extra_headers
        kwargs["additional_chat_options"] = additional_chat_options
        
        # Extract user prompt from messages if available
        if args and len(args) > 0:
            messages = args[0] if isinstance(args[0], list) else None
            if messages:
                for msg in reversed(messages):
                    if hasattr(msg, 'role') and msg.role == 'user' and hasattr(msg, 'content'):
                        self._last_user_prompt = msg.content
                        break
        
        # Clear processed IDs for new run
        self._processed_image_ids.clear()
        
        async for response in super().run_stream(*args, **kwargs):
            # Check if we have image content
            if response.contents:
                for content in response.contents:
                    if isinstance(content, DataContent) and content.media_type.startswith("image/"):
                        # Use content ID to track if we've already processed this specific image
                        content_id = id(content)
                        if content_id in self._processed_image_ids:
                            continue
                            
                        logger.info(f"Processing image content of type: {content.media_type}")
                        try:
                            image_url = None
                            
                            # Check if content has a URL first
                            if hasattr(content, "url") and content.url:
                                logger.info(f"Image DataContent has URL: {content.url}")
                                image_url = content.url
                            else:
                                # Convert to data URI
                                data = content.get_data_bytes()
                                if data:
                                    b64_data = base64.b64encode(data).decode("utf-8")
                                    media_type = content.media_type
                                    image_url = f"data:{media_type};base64,{b64_data}"
                                    logger.info(f"Converted image to data URI (size: {len(data)} bytes)")
                                else:
                                    logger.warning("Image DataContent has no data bytes or URL")
                            
                            # Inject a FunctionCallContent to trigger state update
                            if image_url:
                                prompt = self._last_user_prompt or "Image generated"
                                
                                # Create the image state object
                                image_state = {
                                    "url": image_url,
                                    "prompt": prompt
                                }
                                
                                # Create FunctionCallContent that will trigger state updates
                                function_call = FunctionCallContent(
                                    name="update_image",
                                    call_id=f"call_image_{content_id}",
                                    arguments=json.dumps({"image": image_state})
                                )
                                
                                # Add it to response contents so it flows through the event bridge
                                if not hasattr(response, '_original_contents'):
                                    response._original_contents = response.contents.copy()
                                response.contents.append(function_call)
                                
                                # Mark this image as processed
                                self._processed_image_ids.add(content_id)
                                logger.info(f"Injected update_image tool call for iteration (prompt: {prompt[:50]}...)")
                            
                        except Exception as e:
                            logger.error(f"Failed to process image content: {e}", exc_info=True)
            
            yield response

def create_image_gen_agent(project_client: AIProjectClient):
    """
    Create or get the Image Generation Agent in Azure AI Foundry.
    """
    try:
        # Create a new version of the agent with image generation capabilities
        agent = project_client.agents.create_version(
            agent_name=IMAGE_AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT_NAME,
                instructions=(
                    """Generate images based on user prompts using the image generation tool.
                    If the user asks for something that violates safety policies, politely refuse.
                    always refine the prompt to be more descriptive before generating the image.
                    Before generating an image, think step by step about the details to include in the prompt.
                    Inform the user of the improved prompt before generating the image, and that you will now generate the image."""
                ),
                #### The official docs recommend adding the model here, but currently it's only limted to gpt-image-1 which isn't very helpful.
                #### Hence we set the image model via headers in the ChatAgent subclass.
                tools=[ImageGenTool(quality="low", size="1024x1024", partial_images=2)],
            ),
            description="An agent that generates images based on user prompts.",
        )
        logger.info(f"Created/Updated Image Gen Agent: {agent.id}")
        return agent
    except Exception as e:
        logger.error(f"Error creating image gen agent: {e}")
        # In case of error, try to list and get the latest? 
        # Or just re-raise. For now, re-raise to fail fast.
        raise

def image_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create an image generation agent.

    Args:
        chat_client: The chat client to use for the agent (ignored in favor of specialized client)

    Returns:
        A configured AgentFrameworkAgent instance
    """
    
    if not PROJECT_ENDPOINT:
        logger.error("AZURE_AI_PROJECT_ENDPOINT not set")
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
        
    # 1. Setup Clients
    credential = DefaultAzureCredential()
    sync_project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential
    )
    
    # 2. Create/Get Agent Definition (using sync clients)
    foundry_agent = create_image_gen_agent(sync_project_client)
    
    # 3. Create Async Client for Runtime - Must use async for streaming 
    async_credential = AsyncDefaultAzureCredential()
    async_project_client = AsyncAIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=async_credential
    )
    
    # 4. Create Specialized AzureAIClient
    # Reuse conversation_id if available, otherwise create new - very heplful for debugging and tracing, and very important for multi-turn conversations.
    conversation_id = getattr(chat_client, "conversation_id", None)
    if not conversation_id:
        conversation_id = sync_project_client.get_openai_client().conversations.create().id

    specialized_chat_client = AzureAIClient(
        project_client=async_project_client,
        agent_name=foundry_agent.name,
        agent_version=foundry_agent.version,
        model_deployment_name=MODEL_DEPLOYMENT_NAME,
        conversation_id=conversation_id,
        streaming=True,
    )

    # 5. Create ChatAgent (using subclass)
    agent = ImageGenChatAgent(
        name="image_generation_agent",
        instructions=foundry_agent.definition.instructions,
        chat_client=specialized_chat_client,
        streaming=True,
        #### This added the shared state management tool in addition to the image tool that's already embedded in the foundry agent.
        tools=[update_image],
    )

    return AgentFrameworkAgent(
        agent=agent,
        name="ImageGenerator",
        description="An AI assistant that generates images from text descriptions",
        state_schema={
            "image": {
                "type": "object",
                "description": "The currently generated image",
                "properties": {
                    "url": {"type": "string", "description": "URL or data URI of the image"},
                    "prompt": {"type": "string", "description": "Prompt used to generate the image"},
                },
            },
        },
        predict_state_config={
            "image": {"tool": "update_image", "tool_argument": "image"},
        },
        require_confirmation=False,
    )

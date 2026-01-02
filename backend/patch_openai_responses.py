import logging
from agent_framework.openai._responses_client import OpenAIBaseResponsesClient

logger = logging.getLogger(__name__)

# Capture original method
original_prepare_message = OpenAIBaseResponsesClient._prepare_message_for_openai

def patched_prepare_message_for_openai(self, message, call_id_to_id):
    """
    Patched method to fix payload format for Azure AI Responses API.
    """
    res_list = original_prepare_message(self, message, call_id_to_id)
    
    for msg in res_list:
        # Fix 1: Add 'type': 'message' if missing
        # The Azure AI Responses API requires 'type' field for messages in the input list
        if "type" not in msg:
            msg["type"] = "message"
            
        # Fix 2: For assistant messages, if content is a list of output_text, convert to simple string
        # The API rejects array content for assistant messages with "Value is 'array' but should be 'string'"
        role = msg.get("role")
        content = msg.get("content")
        
        if role == "assistant" and isinstance(content, list):
            # Check if it's a single text item
            if len(content) == 1 and isinstance(content[0], dict) and content[0].get("type") == "output_text":
                msg["content"] = content[0]["text"]
            
    return res_list

def apply_patch():
    """
    Monkeypatch OpenAIBaseResponsesClient._prepare_message_for_openai to fix payload format
    for Azure AI Responses API.
    
    Issues fixed:
    1. Missing 'type': 'message' in message objects.
    2. Assistant messages with array content (should be string for simple text).
    """
    # Check if already patched
    if getattr(OpenAIBaseResponsesClient._prepare_message_for_openai, "_is_patched_for_azure_ai", False):
        logger.info("OpenAIBaseResponsesClient already patched for Azure AI.")
        return

    logger.warning("Applying patch to OpenAIBaseResponsesClient._prepare_message_for_openai")
    patched_prepare_message_for_openai._is_patched_for_azure_ai = True
    OpenAIBaseResponsesClient._prepare_message_for_openai = patched_prepare_message_for_openai

import json
import logging
try:
    from agent_framework_ag_ui._events import AgentFrameworkEventBridge
    from ag_ui.core import ToolCallStartEvent, ToolCallArgsEvent
except ImportError:
    # Fallback if installed differently or using different version structure
    from agent_framework.ag_ui._events import AgentFrameworkEventBridge
    from ag_ui.core import ToolCallStartEvent, ToolCallArgsEvent

from agent_framework import FunctionCallContent, ChatMessage
from agent_framework.openai._responses_client import OpenAIBaseResponsesClient
from itertools import chain
from typing import Any

logger = logging.getLogger(__name__)

def patched_prepare_messages_for_openai(self, chat_messages: list[ChatMessage]) -> list[dict[str, Any]]:
    call_id_to_id: dict[str, str] = {}
    for message in chat_messages:
        for content in message.contents:
            if isinstance(content, FunctionCallContent):
                if (
                    content.additional_properties
                    and "fc_id" in content.additional_properties
                ):
                    call_id_to_id[content.call_id] = content.additional_properties["fc_id"]
                else:
                    # Fallback: use call_id if fc_id is missing
                    # This prevents KeyError when processing tool calls that lost their fc_id
                    # API requires ID to start with 'fc', so we convert 'call_...' to 'fc_...'
                    if content.call_id.startswith("call_"):
                        call_id_to_id[content.call_id] = content.call_id.replace("call_", "fc_", 1)
                    else:
                        call_id_to_id[content.call_id] = f"fc_{content.call_id}"

                    
    list_of_list = [self._prepare_message_for_openai(message, call_id_to_id) for message in chat_messages]
    return list(chain.from_iterable(list_of_list))

def patched_handle_function_call_content(self, content: FunctionCallContent):
    events = []
    if content.name:
        logger.debug(f"Tool call: {content.name} (call_id: {content.call_id})")

    if not content.name and not content.call_id and not self.current_tool_call_name:
        args_length = len(str(content.arguments)) if content.arguments else 0
        logger.warning(f"FunctionCallContent missing name and call_id. args_length={args_length}")

    tool_call_id = self._coalesce_tool_call_id(content)
    
    # PATCH: Only emit start event if it's a NEW tool call ID
    is_new_tool_call = tool_call_id != self.current_tool_call_id
    
    if content.name and is_new_tool_call:
        self.streaming_tool_args = ""
        self.state_delta_count = 0
        
        self.current_tool_call_id = tool_call_id
        self.current_tool_call_name = content.name

        tool_start_event = ToolCallStartEvent(
            tool_call_id=tool_call_id,
            tool_call_name=content.name,
            parent_message_id=self.current_message_id,
        )
        logger.info(f"Emitting ToolCallStartEvent with name='{content.name}', id='{tool_call_id}'")
        events.append(tool_start_event)

        self.pending_tool_calls.append(
            {
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": content.name,
                    "arguments": "",
                },
            }
        )
    elif tool_call_id:
        self.current_tool_call_id = tool_call_id

    if content.arguments:
        delta_str = content.arguments if isinstance(content.arguments, str) else json.dumps(content.arguments)
        logger.info(f"Emitting ToolCallArgsEvent with delta_length={len(delta_str)}, id='{tool_call_id}'")
        args_event = ToolCallArgsEvent(
            tool_call_id=tool_call_id,
            delta=delta_str,
        )
        events.append(args_event)

        for tool_call in self.pending_tool_calls:
            if tool_call["id"] == tool_call_id:
                tool_call["function"]["arguments"] += delta_str
                break

        events.extend(self._emit_predictive_state_deltas(delta_str))
        events.extend(self._legacy_predictive_state(content))

    return events

def apply_patch():
    logger.warning("Applying patch to AgentFrameworkEventBridge._handle_function_call_content")
    AgentFrameworkEventBridge._handle_function_call_content = patched_handle_function_call_content
    
    logger.warning("Applying patch to OpenAIBaseResponsesClient._prepare_messages_for_openai")
    OpenAIBaseResponsesClient._prepare_messages_for_openai = patched_prepare_messages_for_openai

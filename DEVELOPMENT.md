# Development Guide

Advanced guide for customizing and extending the application.

## Project Architecture

### Backend Structure

```
backend/
├── agents/              # Agent implementations
│   ├── simple_agent.py # Basic chat
│   ├── weather_agent.py# Tool rendering example
│   ├── task_agent.py   # Human-in-the-loop example
│   └── recipe_agent.py # Shared state example
├── main.py             # FastAPI server & routing
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

### Frontend Structure

```
frontend/
├── app/
│   ├── api/copilotkit/[agent]/  # API proxy routes
│   ├── chat/
│   │   ├── [agent]/            # Dynamic chat pages
│   │   ├── components/         # Agent-specific components
│   │   │   ├── AgentActions.tsx     # Action hooks
│   │   │   ├── TaskComponents.tsx   # Task UI
│   │   │   ├── WeatherComponents.tsx# Weather UI
│   │   │   └── RecipeComponents.tsx # Recipe UI
│   │   └── style.css          # Chat styles
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page
│   └── globals.css             # Global styles
├── components/
│   └── theme-provider.tsx      # Theme management
└── package.json                # Node dependencies
```

## Creating Custom Agents

### Agent Types Overview

The project includes 4 example agents demonstrating different patterns:

1. **Simple Agent** (`simple_agent.py`) - Basic conversational agent
2. **Weather Agent** (`weather_agent.py`) - Backend tool rendering with custom UI
3. **Task Agent** (`task_agent.py`) - Human-in-the-loop with approval flows
4. **Recipe Agent** (`recipe_agent.py`) - Shared state management with split-screen UI

### 1. Basic Agent

Create `backend/agents/my_agent.py`:

```python
from agent_framework import ChatAgent, ChatClientProtocol
from agent_framework.ag_ui import AgentFrameworkAgent

def my_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    """Create a custom agent."""
    agent = ChatAgent(
        name="my_custom_agent",
        instructions="""You are a helpful assistant that specializes in...
        
        Your capabilities:
        - Capability 1
        - Capability 2
        
        Guidelines:
        - Be clear and concise
        - Always verify information
        """,
        chat_client=chat_client,
    )
    
    return AgentFrameworkAgent(
        agent=agent,
        name="MyAgent",
        description="Description shown in UI",
    )
```

### 2. Agent with Tools

Add tools using the `@ai_function` decorator:

```python
from agent_framework import ChatAgent, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent

@ai_function
def calculate_fibonacci(n: int) -> list[int]:
    """Calculate Fibonacci sequence up to n terms.
    
    Args:
        n: Number of terms to generate
        
    Returns:
        List of Fibonacci numbers
    """
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

@ai_function
async def fetch_data(url: str) -> dict:
    """Fetch data from an API endpoint.
    
    Args:
        url: The API endpoint URL
        
    Returns:
        JSON response as dictionary
    """
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

def math_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    agent = ChatAgent(
        name="math_agent",
        instructions="You help with mathematical calculations.",
        chat_client=chat_client,
        tools=[calculate_fibonacci, fetch_data],
    )
    
    return AgentFrameworkAgent(
        agent=agent,
        name="MathAgent",
        description="Mathematical assistant with tools",
    )
```

### 3. Shared State Agent

Create agents that maintain synchronized state with the UI:

```python
from enum import Enum
from pydantic import BaseModel, Field
from agent_framework import ChatAgent, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    """A task item."""
    title: str = Field(description="Task title")
    priority: Priority = Field(description="Task priority")
    completed: bool = Field(default=False, description="Completion status")

@ai_function
def update_tasks(tasks: list[Task]) -> str:
    """Update the task list.
    
    Args:
        tasks: Complete list of tasks with updates
        
    Returns:
        Confirmation message
    """
    return f"Updated {len(tasks)} tasks"

def task_manager_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    agent = ChatAgent(
        name="task_manager",
        instructions="""You manage a task list. 
        
        To update tasks, call update_tasks with the COMPLETE list.
        Include all existing tasks plus any changes.""",
        chat_client=chat_client,
        tools=[update_tasks],
    )
    
    return AgentFrameworkAgent(
        agent=agent,
        name="TaskManager",
        description="Task management with shared state",
        state_schema={
            "tasks": {"type": "array", "description": "List of tasks"},
        },
        predict_state_config={
            "tasks": {"tool": "update_tasks", "tool_argument": "tasks"},
        },
        require_confirmation=False,
    )
```

### 4. Human-in-the-Loop Agent

Create agents that require human approval:

```python
from pydantic import BaseModel, Field
from agent_framework import ChatAgent, ai_function
from agent_framework.ag_ui import AgentFrameworkAgent, DefaultConfirmationStrategy

class Action(BaseModel):
    """An action to be approved."""
    description: str = Field(description="What this action does")
    risk_level: str = Field(description="low, medium, or high")

@ai_function(
    name="execute_action",
    description="Execute an action that requires approval",
    approval_mode="always_require"  # Requires user approval
)
def execute_action(actions: list[Action]) -> str:
    """Execute a list of actions after approval.
    
    Args:
        actions: List of actions to execute
        
    Returns:
        Execution result
    """
    results = []
    for action in actions:
        # Execute the action
        results.append(f"✓ {action.description}")
    return "\n".join(results)

def approval_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    agent = ChatAgent(
        name="approval_agent",
        instructions="You create action plans that require user approval.",
        chat_client=chat_client,
        tools=[execute_action],
    )
    
    return AgentFrameworkAgent(
        agent=agent,
        name="ApprovalAgent",
        description="Plans actions with human oversight",
        confirmation_strategy=DefaultConfirmationStrategy(),
        require_confirmation=True,
    )
```

## Registering New Agents

1. **Update `backend/agents/__init__.py`:**

```python
from .my_agent import my_agent
from .math_agent import math_agent
from .approval_agent import approval_agent

__all__ = ["my_agent", "math_agent", "approval_agent"]
```

2. **Register in `backend/main.py`:**

```python
from agents import my_agent, math_agent, approval_agent

# Add endpoints
add_agent_framework_fastapi_endpoint(
    app=app,
    agent=my_agent(chat_client),
    path="/myagent",
)

add_agent_framework_fastapi_endpoint(
    app=app,
    agent=math_agent(chat_client),
    path="/math",
)

add_agent_framework_fastapi_endpoint(
    app=app,
    agent=approval_agent(chat_client),
    path="/approval",
)
```

3. **Add to frontend config:**

Update `frontend/app/chat/[agent]/page.tsx` to add agent config:

```typescript
const agentConfig = {
  // ... existing configs
  myagent: {
    title: "My Custom Agent",
    icon: "🤖",
    description: "Your custom agent",
    suggestions: [
      { title: "Example 1", message: "Show me example 1" },
      { title: "Example 2", message: "Show me example 2" },
    ],
    initial: "Hi! I'm your custom agent.",
  },
};
```

4. **Add to homepage:**

Update `frontend/app/page.tsx` to add navigation card:

```typescript
<AgentCard
  href="/chat/myagent"
  title="My Custom Agent"
  description="Your custom agent description"
  icon="🤖"
  color="blue"  // or "indigo", "purple", "green"
/>

// Add color to colorClasses if using new color:
const colorClasses = {
  blue: "from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700",
  // ... other colors
};
```

## Advanced Tool Patterns

### Tools with Streaming

```python
from typing import AsyncGenerator
from agent_framework import ai_function

@ai_function
async def stream_results(query: str) -> AsyncGenerator[str, None]:
    """Stream results as they're generated."""
    for i in range(10):
        await asyncio.sleep(0.5)
        yield f"Result {i}: Processing {query}\n"
```

### Tools with External APIs

```python
import os
import aiohttp
from agent_framework import ai_function

@ai_function
async def get_weather_real(city: str) -> dict:
    """Get real weather data from OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return {
                "temperature": data["main"]["temp"],
                "conditions": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
            }
```

### Tools with State

```python
from agent_framework import ai_function

# Shared state
conversation_history = []

@ai_function
def remember_fact(fact: str) -> str:
    """Remember a fact for later."""
    conversation_history.append(fact)
    return f"Remembered: {fact}"

@ai_function
def recall_facts() -> list[str]:
    """Recall all remembered facts."""
    return conversation_history
```

## Frontend Customization

### Adding Agent to Dynamic Route

Update `frontend/app/chat/[agent]/page.tsx` to add a new agent:

```typescript
const agentConfig = {
  // ... existing configs
  myagent: {
    title: "My Custom Agent",
    icon: "🤖",
    description: "Your custom agent",
    suggestions: [
      { title: "Example 1", message: "Show me example 1" },
      { title: "Example 2", message: "Show me example 2" },
    ],
    initial: "Hi! I'm your custom agent.",
  },
};
```

Then add to homepage `frontend/app/page.tsx`:

```typescript
<AgentCard
  href="/chat/myagent"
  title="My Custom Agent"
  description="Your custom agent description"
  icon="🤖"
  color="blue"
/>
```

### Custom Agent Components

Create custom UI components in `frontend/app/chat/components/`:

```typescript
// MyAgentComponents.tsx
import { useCoAgent } from "@copilotkit/react-core";

interface MyAgentState {
  data: string;
}

export function MyAgentCard() {
  const { state, setState } = useCoAgent<MyAgentState>({
    name: "myagent",
    initialState: { data: "" },
  });

  return (
    <div className="p-6 bg-white dark:bg-gray-800 rounded-xl">
      <h2 className="text-2xl font-bold mb-4">My Agent</h2>
      <input
        value={state.data}
        onChange={(e) => setState({ data: e.target.value })}
        className="w-full p-2 border rounded"
      />
    </div>
  );
}
```

Register in `AgentActions.tsx`:

```typescript
import { MyAgentCard } from "./MyAgentComponents";

export function useMyAgent() {
  // Your agent-specific hooks
  return null;
}
```

### Custom Agent Page

Create `frontend/app/custom/page.tsx`:

```typescript
"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";

export default function CustomPage() {
  return (
    <div className="min-h-screen p-8">
      <CopilotKit runtimeUrl="/api/copilotkit/myagent">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-4">Custom Agent</h1>
          <CopilotChat
            className="h-[600px]"
            labels={{ initial: "Hello! How can I help?" }}
          />
        </div>
      </CopilotKit>
    </div>
  );
}
```

### Custom Tool Rendering

Use `useCopilotAction` for custom tool rendering in `app/chat/components/AgentActions.tsx`:

```typescript
import { useCopilotAction } from "@copilotkit/react-core";

export function useMyToolAction() {
  useCopilotAction({
    name: "my_custom_tool",
    available: "disabled",  // Backend only
    parameters: [
      { name: "data", type: "object", required: true }
    ],
    render: ({ args, result, status }) => {
      if (status !== "complete") {
        return <div className="animate-pulse">Processing...</div>;
      }
      
      return (
        <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <h3 className="font-bold">{args.data.title}</h3>
          <p>{result.message}</p>
        </div>
      );
    },
  });
}
```

Then use in `ChatInterface` component:

```typescript
function ChatInterface({ config, agent }) {
  useBackgroundAction(setBackground);
  useWeatherAction();
  useTaskAction();
  useRecipeAgent();
  useMyToolAction();  // Add your custom action
  
  return <CopilotChat />;
}
```

## Testing

### Backend Testing

Create `backend/tests/test_agents.py`:

```python
import pytest
from agents.simple_agent import simple_agent
from agent_framework.openai import OpenAIChatClient

@pytest.mark.asyncio
async def test_simple_agent():
    client = OpenAIChatClient(model_id="gpt-4o-mini")
    agent = simple_agent(client)
    
    response = await agent.agent.run("Hello!")
    assert response.text
    assert len(response.text) > 0
```

Run tests:
```bash
cd backend
pytest
```

### Frontend Testing

Install testing libraries:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

Create `frontend/__tests__/page.test.tsx`:

```typescript
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Home Page", () => {
  it("renders the main heading", () => {
    render(<Home />);
    expect(screen.getByText(/Agent Framework/i)).toBeInTheDocument();
  });
});
```

## Deployment

### Backend Deployment

**Docker:**

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Environment Variables:**
Set in your deployment platform:
- `OPENAI_API_KEY` or Azure credentials
- `PORT` (default: 8000)

### Frontend Deployment

Deploy to Vercel:

```bash
cd frontend
vercel deploy
```

Set environment variable:
- `BACKEND_URL`: Your backend API URL

## Performance Tips

1. **Use streaming for long responses**
2. **Cache expensive computations**
3. **Use async/await for I/O operations**
4. **Implement rate limiting for API calls**
5. **Use connection pooling for databases**

## Security Best Practices

1. **Never commit `.env` files**
2. **Validate all user inputs**
3. **Use HTTPS in production**
4. **Implement rate limiting**
5. **Sanitize tool outputs**
6. **Use approval mode for sensitive operations**

## Debugging

### Backend Debugging

Enable debug logging:
```bash
conda activate agui
ENABLE_DEBUG_LOGGING=1 python main.py
```

Check logs:
```bash
tail -f ag_ui_server.log
```

### Frontend Debugging

Enable CopilotKit dev console:
```typescript
<CopilotKit
  runtimeUrl="/api/copilotkit/agent"
  showDevConsole={true}  // Enable debug console
>
```

## Resources

- [Agent Framework Docs](https://github.com/microsoft/agent-framework)
- [CopilotKit Docs](https://docs.copilotkit.ai)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)

---

Happy developing! 🚀

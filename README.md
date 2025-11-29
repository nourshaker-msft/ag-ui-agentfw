# Agent Framework + AG-UI + CopilotKit Demo

A full-stack agentic chat application demonstrating the seamless integration of **Microsoft Agent Framework**, **AG-UI**, and **CopilotKit** to create modern, interactive AI agents with beautiful UI rendering and human-in-the-loop capabilities.

![Demo Screenshot](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?style=for-the-badge&logo=typescript)

## 🌟 Features

- **🚀 Real-time Streaming**: Server-sent events for instant agent responses
- **🎨 Beautiful UI**: Backend tool rendering with custom React components
- **🤝 Human-in-the-Loop**: Interactive task planning with approval workflows
- **💬 Multiple Agents**: Simple chat, weather, task planning, and recipe agents
- **🌓 Dark Mode**: Seamless dark/light theme switching
- **⚡ Modern Stack**: Next.js 15, FastAPI, TypeScript, Tailwind CSS
- **🔄 State Management**: Predictive state updates and shared state
- **📱 Responsive Design**: Works beautifully on all devices

**IMPORTANT NOTICE**

This is not a production grade system, please make sure you subject this code to thorough security testing and tuning before attempting to deploy it or adopt it into your systems. This is repository is created using cutting edge technology, which means future releases will bring security fixes and performance improvements, ensure you're always using the latest packages.

This software is offered as is without gurantee or warranty

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │ Home Page  │  │  Chat UI    │  │  API Routes  │         │
│  │            │→ │  (CopilotKit)│→ │   (Proxy)    │         │
│  └────────────┘  └─────────────┘  └──────────────┘         │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/SSE
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │  AG-UI     │→ │    Agent     │→ │   OpenAI/   │         │
│  │  Endpoints │  │  Framework   │  │   Azure AI  │         │
│  └────────────┘  └──────────────┘  └─────────────┘         │
│                                                              │
│  Agents: Simple Chat, Weather, Task Planner, Recipe         │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Tech Stack

### Frontend
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **CopilotKit**: React components for AI chat interfaces
- **Tailwind CSS**: Utility-first styling
- **next-themes**: Dark mode support

### Backend
- **FastAPI**: Modern Python web framework
- **Microsoft Agent Framework**: Agentic orchestration
- **AG-UI**: Agent Framework UI integration
- **Azure OpenAI / OpenAI**: LLM integration
- **Uvicorn**: ASGI server

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm/yarn/pnpm
- **Azure OpenAI credentials** (endpoint, API key, deployment name)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd agentfw
```

### 2. Backend Setup

```bash
cd backend

# Create conda environment
conda create -n agui python=3.11 -y
conda activate agui

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys
```

**Configure `.env`:**

```bash
# Azure OpenAI (required)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install --force
# or
yarn install
# or
pnpm install

# Configure environment
cp .env.example .env.local
# Default backend URL is http://localhost:8000
```

### 4. Run the Application

**Terminal 1 - Start Backend:**

```bash
cd backend
conda activate agui
python main.py
```

Backend will run on `http://localhost:8000`

**Terminal 2 - Start Frontend:**

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### 5. Open Your Browser

Navigate to `http://localhost:3000` and start chatting!

## 🎯 Available Agents

### 💬 Simple Chat Agent
**Endpoint**: `/simple`

A general-purpose conversational AI assistant.

**Features**:
- Natural conversation
- Helpful and friendly responses
- Wide variety of topics

**Try it**: "Tell me a joke" or "Explain quantum computing"

### 🌤️ Weather Agent
**Endpoint**: `/weather`

Get weather information with beautiful UI rendering.

**Features**:
- Weather tool with backend rendering
- Visual weather cards
- Temperature, humidity, wind speed

**Try it**: "What's the weather in San Francisco?"

### ✅ Task Planner Agent
**Endpoint**: `/tasks`

Plan and execute tasks with human oversight.

**Features**:
- Human-in-the-loop interactions
- Step-by-step task planning
- Approval workflows
- Step selection and execution

**Try it**: "Plan a trip to Paris in 8 steps"

### 🍳 Recipe Agent
**Endpoint**: `/shared_state`

Interactive recipe creation with shared state management.

**Features**:
- Split-screen interface with recipe card and chat
- Real-time state synchronization
- Step-by-step recipe building
- Ingredient and instruction management

**Try it**: "Create a recipe for chocolate chip cookies"

## 📂 Project Structure

```
agentfw/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── simple_agent.py      # Simple chat agent
│   │   ├── weather_agent.py     # Weather with tools
│   │   ├── task_agent.py        # Task planning with HITL
│   │   └── recipe_agent.py      # Recipe with shared state
│   ├── main.py                  # FastAPI server
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example            # Environment template
│   └── .gitignore
│
├── frontend/
│   ├── app/
│   │   ├── api/
│   │   │   └── copilotkit/
│   │   │       └── [agent]/
│   │   │           └── route.ts # API proxy
│   │   ├── chat/
│   │   │   ├── [agent]/
│   │   │   │   └── page.tsx    # Chat interface
│   │   │   ├── components/     # Agent UI components
│   │   │   │   ├── AgentActions.tsx
│   │   │   │   ├── TaskComponents.tsx
│   │   │   │   ├── WeatherComponents.tsx
│   │   │   │   └── RecipeComponents.tsx
│   │   │   └── style.css
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   └── theme-provider.tsx  # Theme context
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── .env.example
│   └── .gitignore
│
└── README.md
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Server
PORT=8000

# OpenAI (required if not using Azure)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL_ID=gpt-4o

# Azure OpenAI (optional)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_MODEL_ID=gpt-4

# Logging
ENABLE_DEBUG_LOGGING=0
```

### Frontend Configuration

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000
```

## 🎨 Customization

### Adding a New Agent

1. **Create Agent File** (`backend/agents/my_agent.py`):

```python
from agent_framework import ChatAgent, ChatClientProtocol
from agent_framework.ag_ui import AgentFrameworkAgent

def my_agent(chat_client: ChatClientProtocol) -> AgentFrameworkAgent:
    agent = ChatAgent(
        name="my_agent",
        instructions="Your agent instructions here",
        chat_client=chat_client,
        tools=[],  # Add your tools
    )
    
    return AgentFrameworkAgent(
        agent=agent,
        name="MyAgent",
        description="Agent description",
    )
```

2. **Register in Backend** (`backend/main.py`):

```python
from agents.my_agent import my_agent

add_agent_framework_fastapi_endpoint(
    app=app,
    agent=my_agent(chat_client),
    path="/myagent",
)
```

3. **Add Frontend Route** - Create `frontend/app/chat/myagent/page.tsx` or update the agent config.

### Adding Tools

Create tools with the `@ai_function` decorator:

```python
from agent_framework import ai_function

@ai_function
def my_tool(param: str) -> str:
    """Tool description for the LLM."""
    # Tool implementation
    return f"Result: {param}"
```

## 📚 Learn More

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [AG-UI Documentation](https://github.com/microsoft/agent-framework/tree/main/python/packages/ag-ui)
- [CopilotKit](https://copilotkit.ai)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Microsoft Agent Framework team
- CopilotKit team
- Next.js and Vercel
- FastAPI and Starlette

## 💡 Examples & Use Cases

### Weather Agent with Tool Rendering

The weather agent demonstrates backend tool rendering where the tool execution happens on the server and the UI is rendered on the client:

```python
@AIFunction[Any, dict]
def get_weather(location: str) -> dict:
    return {
        "location": location,
        "temperature": 72,
        "conditions": "sunny",
        "humidity": 65,
        "wind_speed": 10,
        "feels_like": 70
    }
```

### Human-in-the-Loop Task Planning

The task agent shows human-in-the-loop patterns where users can review and approve plans before execution:

```python
@ai_function(
    name="generate_task_plan",
    approval_mode="always_require"
)
def generate_task_plan(task_description: str, steps: list[TaskStep]) -> str:
    return f"Generated {len(steps)} steps for: {task_description}"
```

## 🐛 Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"OpenAI API key not found":**
- Check your `.env` file exists
- Verify `OPENAI_API_KEY` or Azure credentials are set

### Frontend Issues

**"Cannot find module" errors:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Backend connection errors:**
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `backend/main.py`
- Verify `BACKEND_URL` in `.env.local`

## 📞 Support

For issues and questions:
- [Agent Framework Issues](https://github.com/microsoft/agent-framework/issues)
- [CopilotKit Discord](https://discord.gg/copilotkit)

---

Built with ❤️ using Microsoft Agent Framework, AG-UI, and CopilotKit

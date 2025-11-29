# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Checklist

- **Python 3.11+**
- **Node.js 18+** and npm/yarn/pnpm
- **Azure OpenAI credentials**

## Setup (One-time)

### Option 1: Automatic Setup (Recommended)

```bash
./setup.sh
```

This script will:
- Create Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Create environment files

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
conda create -n agui python=3.12 -y
conda activate agui
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API keys
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
```

## Configure API Keys

Edit `backend/.env` and add either:

**OpenAI:**
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_ID=gpt-4o
```

**OR Azure OpenAI:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_MODEL_ID=gpt-4
```

## Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
conda activate agui
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the App

Open your browser to:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Test the Agents

1. Click on any agent card (Simple Chat, Weather, Tasks, or Recipe)
2. Try these prompts:

**Simple Chat:**
- "Tell me a joke"
- "Explain quantum computing"

**Weather Agent:**
- "What's the weather in New York?"
- "How's the weather in Tokyo?"

**Task Planner:**
- "Plan a trip to Paris in 8 steps"
- "Help me learn Python in 10 steps"

**Recipe Agent:**
- "Create a recipe for chocolate chip cookies"
- "Help me make a vegetarian lasagna"

## Troubleshooting

### Backend won't start

```bash
# Make sure you're in the conda environment
cd backend
conda activate agui
which python  # Should show path in conda envs/agui/

# Check dependencies
pip install -r requirements.txt

# Verify API key
cat .env | grep API_KEY
```

### Frontend won't start

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install --force

# Check Node version
node --version  # Should be 18+
```

### Can't connect to backend

1. Verify backend is running on port 8000
2. Check `frontend/.env.local` has `BACKEND_URL=http://localhost:8000`
3. Check browser console for CORS errors

### Port already in use

```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

## Stopping the Application

```bash
./stop.sh
```

Or manually:
- `Ctrl+C` in each terminal
- If using tmux: `tmux kill-session -t agentfw`

## Next Steps

- Customize agents in `backend/agents/`
- Add new tools with `@ai_function` decorator
- Modify UI in `frontend/app/`
- Read the full README.md for advanced features

## Getting Help

- Check the main README.md
- Review backend logs: `backend.log`
- Review frontend logs: `frontend.log`
- Open an issue on GitHub

---

Happy building! 🚀

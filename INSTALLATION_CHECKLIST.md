# Installation Checklist

Use this checklist to ensure everything is set up correctly.

## ✅ Pre-Installation

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm/yarn/pnpm available
- [ ] Git installed (optional, for version control)
- [ ] Have OpenAI API key OR Azure OpenAI credentials ready

## ✅ Setup Steps

### Backend Setup
- [ ] Navigate to `backend/` directory
- [ ] Create conda environment (`conda create -n agui python=3.11 -y`)
- [ ] Activate conda environment
  - `conda activate agui`
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Copy `.env.example` to `.env`
- [ ] Add API key to `.env` file
  - [ ] `OPENAI_API_KEY` (if using OpenAI)
  - OR [ ] Azure credentials (if using Azure OpenAI)

### Frontend Setup
- [ ] Navigate to `frontend/` directory
- [ ] Install dependencies (`npm install`)
- [ ] Copy `.env.example` to `.env.local`
- [ ] Verify `BACKEND_URL` in `.env.local` (default: http://localhost:8000)

## ✅ Verification

### Backend Verification
- [ ] Conda environment is activated (prompt shows `(agui)`)
- [ ] All packages installed successfully (no errors in pip install)
- [ ] `.env` file exists in `backend/`
- [ ] API key is set in `.env` file (not empty)
- [ ] Can run `python main.py` without import errors

### Frontend Verification
- [ ] `node_modules/` directory exists in `frontend/`
- [ ] No errors during `npm install`
- [ ] `.env.local` file exists in `frontend/`
- [ ] Can run `npm run dev` without errors

## ✅ First Run

### Start Backend
- [ ] Terminal 1: `cd backend`
- [ ] Terminal 1: `conda activate agui`
- [ ] Terminal 1: `python main.py`
- [ ] Backend shows "Starting server on http://localhost:8000"
- [ ] No errors in terminal
- [ ] Can access http://localhost:8000 in browser
- [ ] Can access http://localhost:8000/docs (API documentation)

### Start Frontend
- [ ] Terminal 2: `cd frontend`
- [ ] Terminal 2: `npm run dev`
- [ ] Frontend shows "Ready on http://localhost:3000"
- [ ] No compilation errors
- [ ] Can access http://localhost:3000 in browser

## ✅ Test Functionality

### UI Tests
- [ ] Home page loads correctly
- [ ] Three agent cards are visible (Simple Chat, Weather, Tasks)
- [ ] Dark mode toggle works (if implemented)
- [ ] Can click on agent cards

### Agent Tests
- [ ] Can access `/chat/simple` route
- [ ] Can access `/chat/weather` route
- [ ] Can access `/chat/tasks` route
- [ ] Chat interface loads for each agent

### Interaction Tests
- [ ] Can type message in chat
- [ ] Can send message (Enter or Send button)
- [ ] Receives response from agent
- [ ] Response streams in real-time

### Agent-Specific Tests

**Simple Chat:**
- [ ] Send: "Hello"
- [ ] Receives friendly response

**Weather Agent:**
- [ ] Send: "What's the weather in New York?"
- [ ] Receives weather information
- [ ] Weather card renders (if custom rendering implemented)

**Task Planner:**
- [ ] Send: "Plan a trip to Paris in 5 steps"
- [ ] Receives task plan
- [ ] Can approve/modify steps (if HITL implemented)

## ✅ Troubleshooting Completed

If you encountered issues, verify these were resolved:

- [ ] Port 8000 is not in use (backend)
- [ ] Port 3000 is not in use (frontend)
- [ ] CORS is working (no CORS errors in browser console)
- [ ] API key is valid (no 401 errors)
- [ ] All dependencies installed correctly
- [ ] No firewall blocking localhost connections

## ✅ Optional Enhancements

- [ ] Set up git repository (`git init`)
- [ ] Create `.gitignore` (already provided)
- [ ] Set up environment variables for production
- [ ] Configure custom domain (if deploying)
- [ ] Set up monitoring/logging (if deploying)
- [ ] Add tests
- [ ] Set up CI/CD pipeline

## 📝 Notes

Record any issues or customizations here:

```
Issue encountered:


Solution:


Custom changes made:


```

## ✅ Ready for Development

Once all items are checked:
- [ ] Project is fully functional
- [ ] Can start developing custom agents
- [ ] Can customize UI
- [ ] Can add new features
- [ ] Ready to read DEVELOPMENT.md for advanced topics

---

**Date Completed:** _______________

**Completed By:** _______________

**Time Taken:** _______________

## 🎉 Congratulations!

Your Agent Framework + CopilotKit demo is now fully set up and running!

Next steps:
1. Read DEVELOPMENT.md to learn about customization
2. Experiment with the example agents
3. Create your own custom agents
4. Build something amazing!

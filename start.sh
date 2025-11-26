#!/bin/bash

# Start script for Agent Framework + CopilotKit Demo
# Starts both backend and frontend in tmux or separate terminals

set -e

echo "🚀 Starting Agent Framework + CopilotKit Demo"
echo "=============================================="
echo ""

# Check if setup was run
if ! conda env list | grep -q "^agui "; then
    echo "❌ Backend conda environment 'agui' not found. Please run ./setup.sh first"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Please run ./setup.sh first"
    exit 1
fi

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found. Using .env.example"
fi

# Function to start in tmux
start_with_tmux() {
    echo "Starting with tmux..."
    
    # Create new tmux session
    tmux new-session -d -s agentfw
    
    # Backend window
    tmux rename-window -t agentfw:0 'backend'
    tmux send-keys -t agentfw:0 "cd $(pwd)/backend && conda activate agui && python main.py" C-m
    
    # Frontend window
    tmux new-window -t agentfw:1 -n 'frontend'
    tmux send-keys -t agentfw:1 "cd $(pwd)/frontend && npm run dev" C-m
    
    # Attach to session
    echo ""
    echo "✅ Services started in tmux session 'agentfw'"
    echo ""
    echo "📋 Tmux commands:"
    echo "   - Switch windows: Ctrl+b then 0 or 1"
    echo "   - Detach: Ctrl+b then d"
    echo "   - Reattach: tmux attach -t agentfw"
    echo "   - Kill session: tmux kill-session -t agentfw"
    echo ""
    
    sleep 2
    tmux attach -t agentfw
}

# Function to start in background
start_in_background() {
    echo "Starting services in background..."
    
    cd backend
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate agui
    python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "Backend PID: $BACKEND_PID (log: backend.log)"
    echo "Frontend PID: $FRONTEND_PID (log: frontend.log)"
    echo ""
    echo "🌐 Open http://localhost:3000"
    echo ""
    echo "To stop:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    
    # Save PIDs
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
}

# Check for tmux
if command -v tmux &> /dev/null; then
    echo "Found tmux. Starting with tmux..."
    echo "Press Enter to continue or Ctrl+C to cancel"
    read
    start_with_tmux
else
    echo "tmux not found. Starting in background..."
    start_in_background
fi

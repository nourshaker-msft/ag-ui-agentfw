#!/bin/bash

# Stop script for Agent Framework + CopilotKit Demo

echo "🛑 Stopping Agent Framework + CopilotKit Demo"
echo "=============================================="

# Check for tmux session
if tmux has-session -t agentfw 2>/dev/null; then
    echo "Killing tmux session 'agentfw'..."
    tmux kill-session -t agentfw
    echo "✅ Tmux session stopped"
fi

# Check for PID files
if [ -f ".backend.pid" ] && [ -f ".frontend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    FRONTEND_PID=$(cat .frontend.pid)
    
    echo "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend already stopped"
    
    echo "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend already stopped"
    
    rm .backend.pid .frontend.pid
    echo "✅ Background processes stopped"
fi

# Fallback: kill by port
echo "Checking for processes on ports 8000 and 3000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "Killed process on port 8000" || true
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "Killed process on port 3000" || true

echo ""
echo "✅ All services stopped"

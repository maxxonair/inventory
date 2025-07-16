#!/bin/bash

SESSION="servers"

# Define server working directory 
WORKDIR="$HOME/Documents/inventory"

# Remove all active session cookies when the server is restarted
rm $WORKDIR/flask_session/*

# Kill existing session if exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Killing existing tmux session '$SESSION'..."
    tmux kill-session -t $SESSION
fi

# Start a new tmux session in detached mode
tmux new-session -d -s $SESSION

# In pane 0: cd to inventory directory and start InventoryServer
tmux send-keys -t $SESSION "cd $WORKDIR && uv run -m backend.InventoryServer" C-m

# Split window horizontally for second pane
tmux split-window -v -t $SESSION

# In pane 1: cd to inventory directory and start CameraServer
tmux send-keys -t $SESSION "cd $WORKDIR && uv run -m backend.CameraServer" C-m

# Arrange panes
tmux select-layout -t $SESSION even-horizontal

# Attach to session
tmux attach-session -t $SESSION

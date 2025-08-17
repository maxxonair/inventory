#!/bin/bash

SESSION="inventory_services"

# Save project directory
PRJCT_DIR=$PWD

cd ${PRJCT_DIR}/backend/src

# Kill existing session if exists
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Killing existing tmux session '$SESSION'..."
    tmux kill-session -t $SESSION
fi

# Start a new tmux session in detached mode
tmux new-session -d -s $SESSION

# In pane 1: cd to inventory directory and start CameraServer
tmux send-keys -t $SESSION "cd $WORKDIR && OPENCV_AVFOUNDATION_SKIP_AUTH=1 DYLD_LIBRARY_PATH=$(brew --prefix zbar)/lib:$DYLD_LIBRARY_PATH uv run -m camera.CameraServer" C-m

tmux split-window -v -t $SESSION

# In pane 1: cd to inventory directory and start PrinterServer
tmux send-keys -t $SESSION "cd $WORKDIR && uv run -m printer.PrinterServer" C-m

# Arrange panes
tmux select-layout -t $SESSION even-vertical

# Attach to session
tmux attach-session -t $SESSION

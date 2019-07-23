#!/bin/bash
# Script executed at bootup to ensure the bot's started

SHELL=/bin/bash # Ensures bash is used as sh is the default shell

tmux new-session -d "bash"
tmux send -t 0.0 "cd /home/HBB/HumbleBundlesBot/" ENTER
tmux send -t 0.0 "python3 main.py" ENTER

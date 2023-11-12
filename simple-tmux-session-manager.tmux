#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
tmux bind-key C-r run-shell "$CURRENT_DIR/scripts/manager.py restore"
tmux bind-key C-s run-shell "$CURRENT_DIR/scripts/manager.py save"

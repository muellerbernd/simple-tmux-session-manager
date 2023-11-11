#!/usr/bin/env bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
tmux bind-key r run-shell "$CURRENT_DIR/scripts/manager.sh restore"
tmux bind-key C-s run-shell "$CURRENT_DIR/scripts/manager.sh save"

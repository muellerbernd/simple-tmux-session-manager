#!/usr/bin/env python3

import datetime
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

TMUX_SESSION_FILE_PATH = Path("~/.tmux-session").expanduser()
DELIMITER = ";"


# Dry-run flag

DRY_RUN = False


def print_help():
    help_text = """
Tmux session manager

Usage:
  script.py save      - Save current tmux layout to ~/.tmux-session (with backups)
  script.py restore   - Restore tmux sessions from ~/.tmux-session
  script.py help      - Show this help message
  script.py -h|--help - Show this help message

Options:
  -d, --dry-run       Show what would be done without making any changes
"""
    print(help_text.strip())


def read_current_tmux_layout() -> list[str]:
    current_tmux_layout = (
        os.popen(
            f'tmux list-windows -a -F "#S{DELIMITER}#W{DELIMITER}#{{pane_current_path}}"'
        )
        .read()
        .strip()
        .splitlines()
    )
    return current_tmux_layout


def save_layout(dry_run: bool = False):
    if not dry_run:
        os.popen('tmux display-message "saved sessions"')

    if dry_run:
        print("[dry-run] Would save layout to:", TMUX_SESSION_FILE_PATH)
        print("[dry-run] Would read current tmux layout:")
        for l in read_current_tmux_layout():
            print(f"  {l}")
        return

    # Ensure at most two backups exist
    try:
        # Collect existing backups: name matching "<original>*.bak"
        backups = [
            p
            for p in TMUX_SESSION_FILE_PATH.parent.glob(
                TMUX_SESSION_FILE_PATH.name + "*.bak"
            )
        ]
        # Sort by modification time (oldest first)
        backups.sort(key=lambda p: p.stat().st_mtime)
        # Keep only the two most recent backups
        while len(backups) >= 2:
            old = backups.pop(0)
            try:
                old.unlink()
            except Exception as e:
                print(
                    f"Warning: failed to remove old backup {old}: {e}", file=sys.stderr
                )
    except Exception as e:
        # If anything goes wrong with backup cleanup, continue without failing the save
        print(f"{e}")

    if TMUX_SESSION_FILE_PATH.exists():
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_path = TMUX_SESSION_FILE_PATH.with_name(
            TMUX_SESSION_FILE_PATH.name + f".{timestamp}.bak"
        )
        try:
            shutil.copy2(TMUX_SESSION_FILE_PATH, backup_path)
        except Exception as e:
            print(
                f"Warning: failed to create backup {backup_path}: {e}", file=sys.stderr
            )

    with open(TMUX_SESSION_FILE_PATH, "w") as f:
        current_tmux_layout = read_current_tmux_layout()
        for l in current_tmux_layout:
            f.write(l + "\n")


def read_saved_tmux_sessions() -> list[str]:
    target_layout = ""
    # Open the file and read its content.
    with open(TMUX_SESSION_FILE_PATH) as f:
        target_layout = f.read().splitlines()
    return target_layout


def add_window_to_session(session: str, window_name: str, dir: str):
    os.popen(f"tmux new-window -d -t {session}: -n {window_name} -c {dir}")


def create_new_session(session: str, window_name: str, dir: str):
    os.popen(f"cd {dir} && tmux new-session -d -s {session} -n {window_name}")


def session_exists(session: str) -> bool:
    current_tmux_sessions = (
        os.popen('tmux list-sessions -F "#S"').read().strip().splitlines()
    )
    return session in current_tmux_sessions


def restore_layout():
    target_layout = read_saved_tmux_sessions()
    for line in target_layout:
        session, window, dir = line.split(DELIMITER)
        if not session_exists(session):
            create_new_session(session=session, window_name=window, dir=dir)
        else:
            curr_layout = Counter(read_current_tmux_layout())
            target_layout = Counter(target_layout)
            diff = target_layout - curr_layout
            diff_layout = list(diff.elements())
            if f"{session};{window};{dir}" in diff_layout:
                add_window_to_session(
                    session=session,
                    window_name=window,
                    dir=dir,
                )

    os.popen('tmux display-message "restored sessions"')


def main(mode: str):
    global DRY_RUN

    if mode in ("-h", "--help", "help"):
        print_help()
        return

    if mode in ("-d", "--dry-run"):
        DRY_RUN = True
        save_layout(dry_run=DRY_RUN)
        return

    match mode:
        case "save":
            save_layout(dry_run=DRY_RUN)
        case "restore":
            restore_layout()
        case _:
            print("no known command. Use -h/--help for usage.")


if __name__ == "__main__":
    mode = ""
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    main(mode=mode)

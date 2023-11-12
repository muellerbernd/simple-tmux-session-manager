#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import subprocess
from collections import Counter


TMUX_SESSION_FILE_PATH = Path("~/.tmux-session").expanduser()
DELIMITER = ";"


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


def save_layout():
    os.popen('tmux display-message "saved sessions"')
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
        os.popen(
            f'tmux list-sessions -F "#S"'
        )
        .read()
        .strip()
        .splitlines()
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
    match mode:
        case "save":
            save_layout()
        case "restore":
            restore_layout()
        # case "test":
        #     print(session_exists(session="dotfile"))
        case _:
            print("no known command")


if __name__ == "__main__":
    mode = ""
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    main(mode=mode)

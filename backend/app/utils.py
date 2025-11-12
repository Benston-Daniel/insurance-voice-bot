"""Utility helpers for the backend app."""

import os, json

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def log_turn(logfile, data):
    ensure_dir(os.path.dirname(logfile))
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

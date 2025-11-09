"""Utility helpers for the backend app."""

import os


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def read_bytes_from_file(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()

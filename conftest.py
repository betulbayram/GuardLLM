"""Ensures the repo root is importable so tests can `import api`.

The installed package is only ``guardllm``; the ``api`` app lives at the repo
root and is imported directly by the API tests.
"""

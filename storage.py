"""Save a conversation to a JSON file and read it back.

File format (version 1):
    {"version": 1, "messages": [{"role": "system", "content": "..."}, ...]}

Contract: save_conversation writes exactly what load_conversation reads, so
load_conversation(save_conversation(h, path)) == h for any valid history h.
"""
import json
from pathlib import Path

from memory import ConversationFormatError, validate_history

FORMAT_VERSION = 1


def to_json(history):
    """Turn a validated history into a JSON string."""
    validate_history(history)
    return json.dumps({"version": FORMAT_VERSION, "messages": history}, indent=2)


def from_json(text):
    """Turn a JSON string back into a history, or raise ConversationFormatError."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ConversationFormatError(f"file is not valid JSON ({error.msg}, line {error.lineno})")
    if not isinstance(data, dict) or "messages" not in data:
        raise ConversationFormatError("file must be an object with a 'messages' list")
    if data.get("version") != FORMAT_VERSION:
        raise ConversationFormatError(f"unsupported version {data.get('version')!r}")
    return validate_history(data["messages"])


def save_conversation(history, path):
    """Write a history to `path` as UTF-8 JSON and return the path."""
    path = Path(path)
    path.write_text(to_json(history), encoding="utf-8")
    return path


def load_conversation(path):
    """Read a history from `path`. Missing or malformed files raise ConversationFormatError."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConversationFormatError(f"no saved conversation at {path}")
    except UnicodeDecodeError:
        raise ConversationFormatError(f"{path} is not a UTF-8 text file")
    return from_json(text)

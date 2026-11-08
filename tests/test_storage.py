import json

import pytest

from bot import respond
from memory import ConversationFormatError, new_history
from storage import from_json, load_conversation, save_conversation, to_json


def sample_history():
    history = new_history()
    respond(history, "My name is Ana")
    respond(history, 'Say "hi" — with ünïcode')
    return history


def test_round_trip_through_a_file(tmp_path):
    history = sample_history()
    path = save_conversation(history, tmp_path / "chat.json")
    assert load_conversation(path) == history


def test_round_trip_through_a_string():
    history = sample_history()
    assert from_json(to_json(history)) == history


def test_saved_file_has_version_and_messages(tmp_path):
    path = save_conversation(sample_history(), tmp_path / "chat.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["messages"][0]["role"] == "system"


def test_loaded_conversation_keeps_its_memory(tmp_path):
    path = save_conversation(sample_history(), tmp_path / "chat.json")
    restored = load_conversation(path)
    assert respond(restored, "What is my name?") == "Your name is Ana."


def test_missing_file_raises_format_error(tmp_path):
    with pytest.raises(ConversationFormatError, match="no saved conversation"):
        load_conversation(tmp_path / "nope.json")


@pytest.mark.parametrize(
    "text",
    [
        "{not json",
        "[]",
        '{"messages": []}',
        '{"version": 99, "messages": [{"role": "system", "content": "x"}]}',
        '{"version": 1, "messages": [{"role": "system", "content": 5}]}',
    ],
)
def test_malformed_json_raises_format_error(text):
    with pytest.raises(ConversationFormatError):
        from_json(text)

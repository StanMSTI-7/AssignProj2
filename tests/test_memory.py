import pytest

from backend import NO_NAME
from bot import respond
from memory import (
    RECENT,
    ConversationFormatError,
    add_turn,
    new_history,
    request_messages,
    validate_history,
)


def test_new_history_holds_only_the_system_message():
    history = new_history()
    assert len(history) == 1
    assert history[0]["role"] == "system"


def test_each_chat_turn_saves_user_and_assistant_messages():
    history = new_history()
    respond(history, "hello")
    assert [m["role"] for m in history] == ["system", "user", "assistant"]


def test_request_keeps_system_message_and_last_recent_messages():
    history = new_history()
    for i in range(10):
        add_turn(history, "user", f"message {i}")
    sent = request_messages(history)
    assert sent[0] == history[0]
    assert len(sent) == 1 + RECENT
    assert sent[-1]["content"] == "message 9"


def test_bot_remembers_name_inside_the_window():
    history = new_history()
    respond(history, "My name is Ana")
    respond(history, "hello")
    assert respond(history, "What is my name?") == "Your name is Ana."


def test_bot_forgets_name_once_it_leaves_the_window():
    history = new_history()
    respond(history, "My name is Ana")
    respond(history, "hello")
    respond(history, "hi")
    assert respond(history, "What is my name?") == NO_NAME
    assert history[1]["content"] == "My name is Ana"  # still stored, just not sent


def test_add_turn_rejects_unknown_role():
    with pytest.raises(ConversationFormatError):
        add_turn(new_history(), "robot", "beep")


def test_add_turn_rejects_non_text_content():
    with pytest.raises(ConversationFormatError):
        add_turn(new_history(), "user", 42)


@pytest.mark.parametrize(
    "bad",
    [
        [],
        "not a list",
        [{"role": "user", "content": "no system message first"}],
        [{"role": "system"}],
        [{"role": "system", "content": "hi", "extra": 1}],
    ],
)
def test_validate_history_rejects_malformed_data(bad):
    with pytest.raises(ConversationFormatError):
        validate_history(bad)

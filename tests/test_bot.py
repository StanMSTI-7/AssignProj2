from bot import respond
from memory import new_history


def test_blank_input_changes_nothing():
    history = new_history()
    assert respond(history, "   ") == ""
    assert len(history) == 1


def test_unknown_command_is_not_saved_as_a_message():
    history = new_history()
    assert respond(history, "/dance").startswith("Unknown command")
    assert len(history) == 1


def test_reset_clears_back_to_system_message():
    history = new_history()
    respond(history, "hello")
    assert respond(history, "/reset") == "Conversation reset."
    assert history == new_history()


def test_what_did_i_just_say():
    history = new_history()
    respond(history, "I like tea")
    assert respond(history, "What did I just say?") == 'You said: "I like tea"'


def test_save_then_load_command(tmp_path):
    path = tmp_path / "chat.json"
    history = new_history()
    respond(history, "My name is Ana")
    assert respond(history, f"/save {path}").startswith("Saved 3 messages")
    other = new_history()
    assert respond(other, f"/load {path}").startswith("Loaded 3 messages")
    assert other == history


def test_bad_load_keeps_current_conversation(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{oops", encoding="utf-8")
    history = new_history()
    respond(history, "hello")
    before = list(history)
    message = respond(history, f"/load {path}")
    assert message.startswith("Could not load")
    assert history == before

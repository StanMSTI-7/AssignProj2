"""Conversation memory: a list of message dicts that grows one message at a time.

Contract: a history is a list of {"role": str, "content": str} dicts whose
first item is always the system message. Every function here either builds,
checks, or reads that list; none of them prints or touches files.
"""

SYSTEM = "You are a concise, friendly helpdesk assistant."
RECENT = 6  # messages sent after the system message (3 user/assistant exchanges)
ROLES = ("system", "user", "assistant")


class ConversationFormatError(ValueError):
    """Raised when a message or history does not follow the contract above."""


def new_history(system=SYSTEM):
    """Start a conversation that holds only the system message."""
    return [{"role": "system", "content": system}]


def make_message(role, content):
    """Return a validated message dict, or raise ConversationFormatError."""
    if role not in ROLES:
        raise ConversationFormatError(f"unknown role {role!r}; expected one of {ROLES}")
    if not isinstance(content, str):
        raise ConversationFormatError(f"content must be text, got {type(content).__name__}")
    return {"role": role, "content": content}


def add_turn(history, role, content):
    """Validate one message and save it at the end of the history."""
    message = make_message(role, content)
    history.append(message)
    return message


def validate_history(history):
    """Check a whole history (e.g. one read from disk). Returns it unchanged if valid."""
    if not isinstance(history, list) or not history:
        raise ConversationFormatError("history must be a non-empty list of messages")
    for index, message in enumerate(history):
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ConversationFormatError(
                f"message {index} must have exactly the keys 'role' and 'content'"
            )
        make_message(message["role"], message["content"])
    if history[0]["role"] != "system":
        raise ConversationFormatError("the first message must be the system message")
    return history


def request_messages(history, recent=RECENT):
    """The messages actually sent to the backend: the system message plus the last `recent`."""
    return history[:1] + history[1:][-recent:]

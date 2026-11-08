"""Offline stand-in for a model. It answers using only the messages it is given.

Contract: reply(messages) takes the list from memory.request_messages and
returns one string. It never changes the list, so it can later be swapped for
a real model call with the same signature.
"""

NAME_PREFIX = "my name is "
NO_NAME = "I do not know your name yet."
FALLBACK = "Noted. Try 'My name is ...', 'What is my name?', or 'What did I just say?'."


def normalize(text):
    """Lowercase a message and strip surrounding spaces and end punctuation."""
    return text.strip().lower().rstrip("?!.")


def user_texts(messages):
    """Return the content of every user message, oldest first."""
    return [m["content"].strip() for m in messages if m["role"] == "user"]


def find_name(messages):
    """Return the most recent name a user stated, or an empty string."""
    name = ""
    for text in user_texts(messages):
        if text.lower().startswith(NAME_PREFIX):
            name = text[len(NAME_PREFIX):].strip(" .!")
    return name


def previous_user_text(messages):
    """Return the user message before the latest one, or an empty string."""
    texts = user_texts(messages)
    return texts[-2] if len(texts) >= 2 else ""


def reply(messages):
    """Answer the latest user message."""
    latest = normalize(messages[-1]["content"])
    if latest == "what is my name":
        name = find_name(messages)
        return f"Your name is {name}." if name else NO_NAME
    if latest.startswith(NAME_PREFIX):
        return f"Nice to meet you, {find_name(messages)}."
    if latest == "what did i just say":
        previous = previous_user_text(messages)
        return f'You said: "{previous}"' if previous else "This is the first thing you said."
    if latest in ("hi", "hello", "hey"):
        return "Hello! How can I help?"
    return FALLBACK

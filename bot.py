"""Terminal chatbot. Commands: /show, /reset, /save [file], /load [file], /exit."""
from backend import reply
from memory import ConversationFormatError, add_turn, new_history, request_messages
from storage import load_conversation, save_conversation

DEFAULT_FILE = "conversation.json"
HELP = "Commands: /show, /reset, /save [file], /load [file], /exit"


def show(history):
    """Return the stored history as printable lines."""
    return "\n".join(f"[{m['role']}] {m['content']}" for m in history)


def chat_turn(history, text):
    """Save the user's message, get a reply from the recent window, save and return it."""
    add_turn(history, "user", text)
    answer = reply(request_messages(history))
    add_turn(history, "assistant", answer)
    return answer


def run_command(history, command, argument):
    """Handle one slash command. Changes `history` in place and returns what to print."""
    path = argument or DEFAULT_FILE
    if command == "/show":
        return show(history)
    if command == "/reset":
        history[:] = new_history()
        return "Conversation reset."
    if command == "/save":
        return f"Saved {len(history)} messages to {save_conversation(history, path)}."
    if command == "/load":
        try:
            loaded = load_conversation(path)
        except ConversationFormatError as error:
            return f"Could not load: {error}. Current conversation kept."
        history[:] = loaded
        return f"Loaded {len(history)} messages from {path}."
    return f"Unknown command {command}. {HELP}"


def respond(history, text):
    """Handle one line typed by the user and return what to print."""
    text = text.strip()
    if not text:
        return ""
    if text.startswith("/"):
        command, _, argument = text.partition(" ")
        return run_command(history, command, argument.strip())
    return chat_turn(history, text)


def main():
    history = new_history()
    print(f"Prototype chatbot. {HELP}")
    while True:
        try:
            text = input("you > ")
        except (EOFError, KeyboardInterrupt):
            text = "/exit"
        if text.strip() == "/exit":
            print("bye!")
            break
        output = respond(history, text)
        if output:
            print(f"bot > {output}")


if __name__ == "__main__":
    main()

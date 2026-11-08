# Prototype chatbot with saved conversations

An offline terminal chatbot built from small, reusable components. It keeps
conversation memory, saves a conversation to JSON, and reads it back. It uses
only the Python standard library.

```bash
python bot.py          # chat
python -m pytest -q    # run the tests
```

Commands: `/show`, `/reset`, `/save [file]`, `/load [file]`, `/exit`
(the default file is `conversation.json`).

Try: `My name is Ana` → `/save` → `/reset` → `What is my name?` → `/load` → `What is my name?`

## Components and their contracts

| File | Responsibility | Input → output |
| --- | --- | --- |
| `memory.py` | Build and check the history | `new_history() → list`; `add_turn(history, role, content) → message` (validates, appends); `validate_history(history) → history` or raises; `request_messages(history, recent=6) → list` |
| `backend.py` | Produce a reply (a stand-in for a model) | `reply(messages) → str`; it never changes `messages` |
| `storage.py` | Turn a history into JSON and back | `save_conversation(history, path) → Path`; `load_conversation(path) → history` or raises |
| `bot.py` | Terminal I/O and commands | `respond(history, text) → str` for printing; `chat_turn` and `run_command` do the work |

**What they share:** a history is a list of `{"role", "content"}` dicts, and the
first one is always the system message. Every component reads or writes that
shape. Bad data raises one error type, `ConversationFormatError` (a `ValueError`).

### What was refactored from the week-3 memory bot
- In `respond`, the three repeated `text.strip() == ...` checks became one
  `partition` followed by `run_command`. `chat_turn` now holds the user → reply → assistant steps.
- In `backend.py`, the repeated "loop over user messages" logic became `user_texts`,
  and `find_name` and `previous_user_text` both use it.
- The memory behavior is the same: the full history is stored, but only the
  system message plus the last `RECENT = 6` messages are sent to `reply`.
  Tests cover both remembering and forgetting a name.

## Error handling
- `add_turn` rejects an unknown role or content that isn't text.
- `load_conversation` / `from_json` turn every bad-file case into
  `ConversationFormatError` with a readable message: missing file, non-UTF-8
  bytes, invalid JSON, the wrong top-level shape, an unsupported `version`, or
  malformed messages.
- `/load` catches that error and **keeps the current conversation**, so a broken
  file never wipes your chat.

## Serialization format
```json
{"version": 1, "messages": [{"role": "system", "content": "..."}, ...]}
```
`load_conversation(save_conversation(h, p)) == h` (tested, including Unicode and quotes).

## Design choice
**Plain dicts and a shared validator instead of a `Conversation` class.** The
history keeps the exact `{"role", "content"}` shape that chat-model APIs use, so
it can go straight to `json.dumps` or to a real model. `validate_history` is the
single gatekeeper. Both `add_turn` (new data) and `load_conversation` (data
from disk) use it, so in-memory and saved data follow the same rules.
Swapping `backend.reply` for a real model call needs no other changes.

The `version` field is there so the format can change later without silently
misreading old files.

## Limitations
- **Fixed message-count window.** Memory is "the last 6 messages", not the last N
  tokens or the important facts. A name given three exchanges back is forgotten even
  though it is still stored (see `test_bot_forgets_name_once_it_leaves_the_window`).
  A real bot would summarize old turns or extract facts.
- **Rule-based replies.** The backend only recognizes a few exact phrases
  (`What is my name?`, `My name is ...`, `What did I just say?`, greetings).
- **No safe-write or locking.** `/save` overwrites the file directly. A crash
  mid-write or two bots saving to the same file could corrupt it, though the
  loader would then report the damage instead of crashing.

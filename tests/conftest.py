"""Let the tests import bot, memory, backend and storage from the folder above."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

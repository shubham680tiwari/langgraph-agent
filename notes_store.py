# notes_store.py: a tiny local notes database (a JSON file). Plain Python, no LangGraph.
import json
from datetime import datetime
from pathlib import Path

# The data/ folder sits next to this file, so it works wherever you run Python from.
NOTES_FILE = Path(__file__).parent / 'data' / 'notes.json'


def load_notes() -> list[dict]:
    """Return every saved note, oldest first. An empty list if there are none yet."""
    if not NOTES_FILE.exists():
        return []
    return json.loads(NOTES_FILE.read_text(encoding='utf-8'))


def add_note(text: str) -> dict:
    """Save one note to the file and return it."""
    notes = load_notes()
    next_id = max((note['id'] for note in notes), default=0) + 1   # safe even after deletions
    note = {
        'id': next_id,
        'text': text,
        'created_at': datetime.now().isoformat(timespec='seconds'),
    }
    notes.append(note)
    NOTES_FILE.parent.mkdir(exist_ok=True)      # create data/ the first time
    # ensure_ascii=False keeps non-English text (Hindi, for example) readable in the file.
    NOTES_FILE.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding='utf-8')
    return note
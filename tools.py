from datetime import datetime

from langchain.tools import tool
from notes_store import add_note, load_notes

@tool(parse_docstring=True)
def save_note(text: str) -> str:
    """Save a note for the user in their local files
        Use this when the user asks to remeber, note down or write something.

        Args:
        text: The note to save, written clearly in one or two sentences
    
    """
    note = add_note(text)
    note_id = note['id']
    return f'Saved note #{note_id}'


@tool
def list_notes()-> str:
    """List every notes the user has saved, each with its number"""
    notes = load_notes()
    if not notes:
        return 'There are no saved notes'

    lines = []

    for note in notes:
        note_id = note['id']
        note_text = note['text']
        lines.append(f'{note_id}. {note_text}')

    return '\n'.join(lines)


@tool
def get_current_time() -> str:
    """ Get the current local time and date. Use it for 
    any question about now, today or the time"""
    return datetime.now().strftime('%A, %d %B %Y, %I:%M %p')

ALL_TOOLS = [save_note, list_notes, get_current_time]
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

class NoteState(TypedDict):
    raw_text: str
    clean_text: str
    priority: str
    summary: str

# Node 1
def clean_note(state: NoteState) -> dict:
    # '    hello  there.   '
    cleaned = ' '.join(state['raw_text'].split())
    return {'clean_text': cleaned}

# Node 2
def check_priority(state: NoteState) -> dict:
    high_priority_words = ('urgent', 'asap', 'today')
    text = state['clean_text'].lower() # hello there
    priority = 'high' if any(word in text for word in high_priority_words) else 'normal'
    return {'priority': priority}

# Node 3
def note_summary(state: NoteState) -> dict:
    tag = '[!]' if state['priority'] == 'high' else '[ ]'
    text = state['clean_text']
    return {'summary': f'{tag}{text}'}


# Graph

graph = StateGraph(NoteState)
graph.add_node("clean_note", clean_note)
graph.add_node("check_priority", check_priority)
graph.add_node("note_summary", note_summary)

# Edges
graph.add_edge(START, "clean_note")

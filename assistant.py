# assistant.py: version 0.2. Nova routes each message to the right skill.
from datetime import datetime
from typing import Literal

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from llm import get_llm, text_of
from notes_store import add_note, load_notes

llm = get_llm()


# STATE: the conversation (with add_messages) plus two whiteboard keys that
# the classifier writes and the later nodes read.
class AssistantState(MessagesState):
    intent: str       # 'chat', 'save_note' or 'list_notes'
    note_text: str    # the note to store (only filled for save_note)


# The exact answer we require from the classifier.
class Intent(BaseModel):
    intent: Literal['chat', 'save_note', 'list_notes'] = Field(
        description=(
            'save_note: the user wants something remembered or written down. '
            'list_notes: the user wants to see their saved notes. '
            'chat: anything else.'
        )
    )
    note_text: str = Field(
        default='',
        description='For save_note only: the note itself, without phrases like save a note. Otherwise empty.',
    )


intent_classifier = llm.with_structured_output(Intent)


def build_system_prompt() -> str:
    today = datetime.now().strftime('%A, %d %B %Y')
    return (
        "You are Nova, a friendly personal assistant running on the user's own computer. "
        'Keep answers short: at most three sentences unless asked for more. '
        f'Today is {today}.'
    )


# NODE 1: decide what the user wants and WRITE the decision into the state.
def classify_intent(state: AssistantState) -> dict:
    latest = text_of(state['messages'][-1])     # the newest user message
    try:
        result = intent_classifier.invoke(f'Decide what the user wants. User message: {latest}')
        return {'intent': result.intent, 'note_text': result.note_text}
    except Exception:
        # If classification fails, fall back to plain chat so Nova still answers.
        return {'intent': 'chat', 'note_text': ''}


# ROUTER: only READS the decision. The path map in build_graph turns labels into nodes.
def route_by_intent(state: AssistantState) -> str:
    return state['intent']


# NODE 2a: chat. This is the Session 2 behaviour, unchanged.
def call_model(state: AssistantState) -> dict:
    messages = [SystemMessage(build_system_prompt())] + state['messages']
    return {'messages': [llm.invoke(messages)]}


# NODE 2b: save a note. Plain Python, no LLM. It replies with an AIMessage so the
# conversation history stays complete.
def save_note_node(state: AssistantState) -> dict:
    text = state['note_text'].strip()
    if not text:
        return {'messages': [AIMessage('What would you like me to note down?')]}
    note = add_note(text)
    note_id = note['id']
    return {'messages': [AIMessage(f'Saved note #{note_id}: {text}')]}


# NODE 2c: list the saved notes.
def list_notes_node(state: AssistantState) -> dict:
    notes = load_notes()
    if not notes:
        return {'messages': [AIMessage('You have no saved notes yet.')]}
    lines = []
    for note in notes:
        note_id = note['id']
        note_text = note['text']
        lines.append(f'{note_id}. {note_text}')
    return {'messages': [AIMessage('Your notes:\n' + '\n'.join(lines))]}


def build_graph():
    builder = StateGraph(AssistantState)
    builder.add_node('classify_intent', classify_intent)
    builder.add_node('call_model', call_model)
    builder.add_node('save_note_node', save_note_node)
    builder.add_node('list_notes_node', list_notes_node)

    builder.add_edge(START, 'classify_intent')
    builder.add_conditional_edges(
        'classify_intent',            # the router runs right after this node
        route_by_intent,              # returns the label stored in state['intent']
        {                             # label -> node name
            'chat': 'call_model',
            'save_note': 'save_note_node',
            'list_notes': 'list_notes_node',
        },
    )
    builder.add_edge('call_model', END)
    builder.add_edge('save_note_node', END)
    builder.add_edge('list_notes_node', END)
    return builder.compile()


def chat() -> None:                   # the Session 2 loop, unchanged
    graph = build_graph()
    history = []
    print('Nova is ready. Type quit to exit.')
    while True:
        user_text = input('You: ').strip()
        if user_text.lower() in ('quit', 'exit'):
            break
        if not user_text:
            continue
        history.append(HumanMessage(user_text))
        result = graph.invoke({'messages': history})
        history = result['messages']
        print('Nova:', text_of(history[-1]))


if __name__ == '__main__':
    chat()
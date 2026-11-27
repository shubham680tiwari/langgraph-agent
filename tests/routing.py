from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class TempState(TypedDict):
    text: str
    category: str # decision
    reply: str

# Node 1
def categorize(state: TempState) -> dict:
    text = state['text'].lower().strip()
    if text.endswith('?'):
        category = 'question'
    elif text.startswith(('remind', 'todo', 'task')):
        category = 'task'
    else:
        category = 'other'
    return {'category': category}

# Router or fork
def pick_node(state: TempState)-> Literal['answer_question', 'complete_task', 'normal']:
    if state['category'] == 'question':
        return 'answer_question'
    if state['category'] == 'task':
        return 'complete_task'
    if state['category'] == 'other':
        return 'normal'

# Node 2
def answer_question(state: TempState) -> dict:
    return {'reply': 'Good question, this is the answer'}

# Node 3
def complete_task(state: TempState)-> dict:
    return {'reply': 'Task completed'}

# Node 4
def normal(state: TempState)-> dict:
    return {'reply': 'Hello, thanks for contacting'}

graph = StateGraph(TempState)
graph.add_node(categorize)
graph.add_node(answer_question)
graph.add_node(complete_task)
graph.add_node(normal)

graph.add_edge(START, 'categorize')

# conditional edge
graph.add_conditional_edges('categorize', pick_node)

graph.add_edge('answer_question', END)
graph.add_edge('complete_task', END)
graph.add_edge('normal', END)

agent = graph.compile()

for step in agent.stream({'text': 'What is langgraph?'}, stream_mode='updates'):
    print(step)

# print(agent.get_graph().draw_mermaid())
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# 1. State
class GreeteState(TypedDict):
    name: str
    greeting: str   # Hello Alex

# 2. Node
# receives the current state and returns only the key-value it changes
def greet(state: GreeteState) -> dict:
    name = state['name']
    return {'greeting': f'Hello {name}'}

# 3. Graph
graph = StateGraph(GreeteState)
graph.add_node('greet', greet)
graph.add_edge(START, 'greet')
graph.add_edge('greet', END)

# 4. compile

app = graph.compile()

result = app.invoke({'name': 'Alex'})

print(result)
# print(app.get_graph().draw_mermaid())

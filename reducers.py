import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

class LogState(TypedDict):
    # ANnnotated[type, reducer]: every update to log is combined using operator.add
    log: Annotated[list[str], operator.add]
    status: str

def step_one(state: LogState) -> dict:
    return {
        'log': ['step one finished'],
        'status': 'half done'
    }

def step_two(state: LogState) -> dict:
    return {
        'log': ['step two finished'],
        'status': 'done'
    }

graph = (
    StateGraph(LogState)
    .add_node(step_one)
    .add_node(step_two)
    .add_edge(START, 'step_one')
    .add_edge('step_one', 'step_two')
    .add_edge('step_two', END)
    .compile()
)

result = graph.invoke({'log': ['graph started'], 'status': 'new'})

print(result['log'])
print(result['status'])
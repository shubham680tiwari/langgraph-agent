from langchain.messages import HumanMessage
from langchain.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from llm import get_llm


# @tool turns a normal function into a tool. Name, type hintsand the docstring becomes the description for the model
@tool
def add(a:int, b:int) -> int:
    """Addtwo whole numbers"""
    return a + b


@tool
def multiply(a:int, b:int) -> int:
    """Multiply two whole numbers"""
    return a * b


tools=[add, multiply]

tools_by_name = {t.name: t for t in tools}

llm_with_tools = get_llm().bind_tools(tools)

def call_model(state: MessagesState) -> dict:
    # The model returns the whole conversation and either answers or asks for tools
    return {'messages': [llm_with_tools.invoke(state['messages'])]}

def run_tools(state: MessagesState) -> dict:
    last_message = state['messages'][-1]
    results = []
    for call in last_message.tool_calls:
        tool_to_run = tools_by_name[call['name']]
        results.append(tool_to_run.invoke(call))

    return {'messages': results}

# Router: check if last AI message asks for tools
def has_tool_calls(state: MessagesState) -> str:
    last_message = state['messages'][-1]
    return 'tools' if last_message.tool_calls else 'done'


graph = (
    StateGraph(MessagesState)
    .add_node(call_model)
    .add_node('tools', ToolNode(tools))
    .add_edge(START, 'call_model')
    .add_conditional_edges('call_model', tools_condition)
    .add_edge('tools', 'call_model')
    .compile()
    )


result = graph.invoke({'messages': [HumanMessage('What is 17 times 23 plus 5?')]})
for message in result['messages']:
    message.pretty_print()

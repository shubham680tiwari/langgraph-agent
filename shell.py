from langchain.messages import HumanMessage
from assistant import build_graph
from llm import text_of

graph = build_graph()
print(graph.get_graph().draw_mermaid())      # draw it: START -> call_model -> END

result = graph.invoke({'messages': [HumanMessage('Hi! What can you help me with?')]})
for message in result['messages']:
    message.pretty_print()
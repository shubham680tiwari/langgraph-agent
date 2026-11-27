from langchain.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

history = [HumanMessage('hi')]

history = add_messages(history, [AIMessage('How can I help you?')])

history = add_messages(history, [{'role': 'user', 'content': 'What is Langgraph?'}])

for message in history:
    message.pretty_print()

print(len(history))
print(history[0].id)
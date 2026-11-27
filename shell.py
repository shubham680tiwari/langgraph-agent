# from langchain.messages import HumanMessage
# from assistant import build_graph
# from llm import text_of

# graph = build_graph()
# print(graph.get_graph().draw_mermaid())      # draw it: START -> call_model -> END

# result = graph.invoke({'messages': [HumanMessage('Hi! What can you help me with?')]})
# for message in result['messages']:
#     message.pretty_print()




from tools import save_note, list_notes, get_current_time

print(get_current_time.invoke({}))                    # tools take a dict of arguments
print(save_note.invoke({'text': 'test note'}))        # Saved note #1.
print(list_notes.invoke({}))
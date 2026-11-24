from datetime import datetime

from langchain.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph

from llm import get_llm, text_of

llm = get_llm()


def chat() -> None:
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

        print('Nova: ', end='')
        full_reply = ''

        for chunk, metadata in graph.stream({'messages': history}, stream_mode='messages'):
            is_token = isinstance(chunk, AIMessageChunk)
            from_our_node = metadata.get('langgraph_node') == 'call_model'

            if is_token and from_our_node:
                piece = text_of(chunk)
                print(piece, end='', flush=True)
                full_reply += piece

        print()
        history.append(AIMessage(full_reply))


def build_system_prompt() -> str:
    today = datetime.now().strftime('%A, %d %B %Y')

    return (
        "You are Nova, a friendly personal assistant running on the user's own computer. "
        "Keep answers short: at most three sentences unless asked for more. "
        f"Today is {today}."
    )


def call_model(state: MessagesState) -> dict:
    messages = [SystemMessage(build_system_prompt())] + state['messages']

    reply = llm.invoke(messages) # returns AIMessage

    return {'messages': [reply]}


def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node('call_model', call_model)
    graph.add_edge(START, 'call_model')
    graph.add_edge('call_model', END)
    return graph.compile()


if __name__ == '__main__':                    # runs only with: python assistant.py
    chat()
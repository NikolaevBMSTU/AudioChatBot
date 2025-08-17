import os
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    request_txt: str
    response_txt: str
    response_audio: str


graph_builder = StateGraph(State)


from chatbot.CustomOllamaLLM import CustomOllamaLLM
from chatbot.CustomOllamaLLM import CustomLLMConfig

config = CustomLLMConfig(
    api_url=os.getenv("OLLAMA_API_URL").strip(),
    username=os.getenv("OLLAMA_LOGIN").strip(),
    password=os.getenv("OLLAMA_PASSWORD").strip()
)

llm = CustomOllamaLLM(config=config)


def chatbot(state: State):
    state["response_txt"] = llm._call(state["request_txt"])
    return state


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream(State(request_txt=user_input)):
        for value in event.values():
            print("Assistant:", value["response_txt"])


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        # user_input = "What do you know about LangGraph?"
        # print("User: " + user_input)
        # stream_graph_updates(user_input)
        print("Something went wrong")
        break

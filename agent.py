import os
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    request_txt: str
    response_txt: str
    response_audio: str


graph_builder = StateGraph(State)


from chat_bot.CustomOllamaLLM import CustomOllamaLLM
from chat_bot.CustomOllamaLLM import CustomLLMConfig

config = CustomLLMConfig(
    api_url=os.getenv("OLLAMA_API_URL"),
    username=os.getenv("OLLAMA_LOGIN"),
    password=os.getenv("OLLAMA_PASSWORD")
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

# Compiled graph visualization (optional)
try:
    with open("graph.png", "wb") as png:
        png.write(graph.get_graph().draw_mermaid_png())
except Exception:
    pass

def agent_invoke(user_input: str):
    return graph.invoke(State(request_txt=user_input))["response_txt"]

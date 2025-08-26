import os
from dotenv import load_dotenv

from requests.auth import HTTPBasicAuth

from typing import Annotated
from typing_extensions import TypedDict

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    # request_txt: str
    # response_txt: str
    # response_audio: str

auth_config = HTTPBasicAuth(os.getenv("OLLAMA_LOGIN"), os.getenv("OLLAMA_PASSWORD"))

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", 'llama3.2'),
    base_url=os.getenv("OLLAMA_API_URL"),
    client_kwargs={"auth": auth_config},
    async_client_kwargs={"auth": auth_config}
)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory, debug=True)

# Compiled graph visualization (optional)
try:
    with open("graph.png", "wb") as png:
        png.write(graph.get_graph().draw_mermaid_png())
except Exception:
    pass

class WorkingGraph:
    def __init__(self):
        self.memory = memory
        self.graph = graph

    def invoke(self, user_id: str, user_input: str):
        config = {"configurable": {"thread_id": user_id}}
        events = self.graph.stream({"messages": [HumanMessage(user_input)]}, config)
        for event in events:
            for value in event.values(): 
                return value["messages"][-1].content

    def clear_memory(self, user_id: str):
        self.graph.checkpointer.delete_thread(thread_id=user_id)

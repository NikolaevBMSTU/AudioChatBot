import os

from requests.auth import HTTPBasicAuth

from langchain_ollama import ChatOllama
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage

from langchain.agents.middleware import before_model, HumanInTheLoopMiddleware
from langgraph.runtime import Runtime
from langgraph.types import Command

from langgraph.checkpoint.memory import InMemorySaver

from tools import search_web, search_wikipedia
import prompts

auth_config = HTTPBasicAuth(os.getenv("OLLAMA_LOGIN"), os.getenv("OLLAMA_PASSWORD"))

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", 'llama3.2'),
    base_url=os.getenv("OLLAMA_API_URL"),
    client_kwargs={"auth": auth_config},
    async_client_kwargs={"auth": auth_config},
)


@before_model
def messages_logging(state: AgentState, runtime: Runtime) -> None:
    messages = state["messages"]

    with open(f"bot_.log", 'a', encoding='utf-8') as file:
        file.write(str(messages) + "\n")

    return


agent = create_agent(
    llm,
    middleware=[
        SummarizationMiddleware(
            llm,
            max_tokens_before_summary=500,
            messages_to_keep=10
        ),
        messages_logging
    ],
    tools=[search_web, search_wikipedia],
    checkpointer=InMemorySaver(),
    system_prompt=prompts.de_lehrer_system_prompt
)

class ChatBot:
    def __init__(self):
        self.agent = agent

    def invoke(self, user_id: str, user_input: str):
        config = {"configurable": {"thread_id": user_id}}
        return self.agent.invoke({"messages": [HumanMessage(user_input)]}, config)
    
    def approve_action(self, user_id: str, user_decision: str):
        config = {"configurable": {"thread_id": user_id}}
        return self.agent.invoke(Command(resume={"decisions": [{"type": user_decision}]}), config)

    def clear_memory(self, user_id: str):
        self.agent.checkpointer.delete_thread(thread_id=user_id)

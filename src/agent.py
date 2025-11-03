import os

from requests.auth import HTTPBasicAuth

from langchain_ollama import ChatOllama
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage

from langchain_community.document_loaders import WikipediaLoader
from langchain_tavily import TavilySearch
from langchain.tools import tool

from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime

from langgraph.checkpoint.memory import InMemorySaver

auth_config = HTTPBasicAuth(os.getenv("OLLAMA_LOGIN"), os.getenv("OLLAMA_PASSWORD"))

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", 'llama3.2'),
    base_url=os.getenv("OLLAMA_API_URL"),
    client_kwargs={"auth": auth_config},
    async_client_kwargs={"auth": auth_config},
)

@tool
def search_web(query: str):
    
    """ Tools for retrieve docs from web search if you need specific information about current situation"""

    # Search
    tavily_search = TavilySearch(max_results=1)
    search_docs = tavily_search.invoke(query)

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
            for doc in search_docs['results']
        ]
    )

    return {"context": [formatted_search_docs]}

@tool
def search_wikipedia(query: str):
    
    """ Retrieve docs from wikipedia """

    # Search
    search_docs = WikipediaLoader(query, load_max_docs=2).load()

     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}">\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

de_lehrer_system_prompt = """
    Sie sind eine erfahrene Deutschlehrer für internationale Schüler.
    Beantworten Sie die Frage so, dass sie auch für Schüler auf A2-Niveau verständlich ist.
    Verwenden Sie keine Tabellen zur Beantwortung der Fragen.
    """
de_text_check_prompt = """
    Überprüfen Sie Ihren geschriebenen Text und korrigieren Sie Grammatik-, Wortschatz- und Rechtschreibfehler.
    ```
    {text}
    ```
    Stellen Sie eine oder mehrere Fragen zum Text, um das Gespräch am Laufen zu halten, oder geben Sie eine Sprachlernaufgabe.
    """

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
    tools=[search_web],
    checkpointer=InMemorySaver(),
    system_prompt=de_lehrer_system_prompt
)

class ChatBot:
    def __init__(self):
        self.agent = agent

    def invoke(self, user_id: str, user_input: str):
        config = {"configurable": {"thread_id": user_id}}
        return self.agent.invoke({"messages": [HumanMessage(de_text_check_prompt.format(text=user_input))]}, config)

    def clear_memory(self, user_id: str):
        self.agent.checkpointer.delete_thread(thread_id=user_id)

from langchain_community.document_loaders import WikipediaLoader
from langchain_tavily import TavilySearch
from langchain.tools import tool

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

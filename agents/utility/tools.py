from .file import create_file_tool, read_file_tool, delete_file_tool
from .application import launch_application_tool, close_application_tool
from .system import set_volume_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from .math_tools import get_math_tool
from langchain_groq import ChatGroq
import getpass
import os


def _get_pass(var: str):
    if var not in os.environ:
        os.environ[var] = getpass.getpass(f"{var}: ")


_get_pass("GROQ_API_KEY")

_get_pass("TAVILY_API_KEY")

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
calculate = get_math_tool(llm)
search = TavilySearchResults(
    max_results=1,
    description='tavily_search_results_json(query="the search query") - a search engine.',
)

tools = [search, calculate, create_file_tool, read_file_tool, delete_file_tool, set_volume_tool, launch_application_tool, close_application_tool]
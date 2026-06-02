import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# Load environment
load_dotenv()

# Set API keys
OPENAI_API_KEY = os.getenv("openai_api_key", os.getenv("OPENAI_API_KEY", ""))
TAVILY_API_KEY = os.getenv("tavily_api_key", os.getenv("TAVILY_API_KEY", ""))

if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
if TAVILY_API_KEY:
    os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Initialize search tools
tavily_search = TavilySearch(max_results=3)

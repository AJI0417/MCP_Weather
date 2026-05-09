import os
import getpass
from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_ollama.chat_models import ChatOllama #ollama LLM
from langchain.agents import create_agent
from dotenv import load_dotenv
from ai.tools import search_knowledge_base
from ai.prompt import SYSTEM_PROMPT
from mcp_client.mcp_client import get_mcp_client


load_dotenv()
API_KEY = os.getenv("gemini_api_key")

os.environ["GOOGLE_API_KEY"] = getpass.getpass(API_KEY)

def create_my_agent():

    # llm = ChatOllama(
    #     model="gemma4:e4b",
    #     temperature = 1.0
    # )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-pro-preview",
        api_key = API_KEY,
        temperature=1.0,  # Gemini 3.0+ defaults to 1.0
        thinking_level="low",
    )


    client = get_mcp_client()

    async def build():
        tools = await client.get_tools()
        tools.append(search_knowledge_base)

        agent = create_agent(
            llm,
            tools,
            system_prompt=SYSTEM_PROMPT
        )

        return agent

    return build
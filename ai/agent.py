from langchain_ollama.chat_models import ChatOllama
from langchain.agents import create_agent

from ai.tools import search_knowledge_base
from ai.prompt import SYSTEM_PROMPT
from mcp_client.mcp_client import get_mcp_client


def create_my_agent():

    model = ChatOllama(
        model="qwen3.5:4b",
        temperature=0
    )

    client = get_mcp_client()

    async def build():
        tools = await client.get_tools()
        tools.append(search_knowledge_base)

        agent = create_agent(
            model,
            tools,
            system_prompt=SYSTEM_PROMPT
        )

        return agent

    return build
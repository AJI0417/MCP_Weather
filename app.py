import chainlit as cl
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain.agents import create_agent


LLM_MODEL = "llama3.1:latest"
SYSTEM_PROMPT = """你是一個嚴格遵守流程的專業助理，請「一步一步」完成任務。
【強制規則（不可違反）】
1. 任何情況下，只要使用者的需求涉及「天氣」，
   你必須【先】呼叫 weather MCP tool 查詢天氣。

【決策規則（必須遵守）】
- 若 用戶指令有包括『晴天』相關訊息 = 你必須呼叫 push_sunny_message
- 若 用戶指令有包括『雨天』相關訊息 = 你必須呼叫 push_rainy_message
- 若 用戶指令有包括『颱風』相關訊息 = 你必須呼叫 push_typhoon_message
- 不得自行生成推播內容，必須實際呼叫對應 MCP tool

【禁止事項】
- 不得假設推送成功
- 不得自行輸出「已推送」之類的文字
- 在 MCP tool 呼叫完成後，向用戶說明呼叫了哪個MCP Tool。

請嚴格依照以上規則執行。
"""

# ========== RAG ==========

# file_path = "./example_data/layout-parser-paper.pdf"
# loader = PyPDFLoader(file_path)

# embeddings = OllamaEmbeddings(
#     model="nomic-embed-text:latest",
# )


# LLM
model = ChatOllama(
    model=LLM_MODEL,
    temperature=0,
)

# MCP Client
client = MultiServerMCPClient(
    {
        "LINE_Notify": {
            "transport": "streamable-http",
            "url": "http://127.0.0.1:8001/mcp",
        },
        "Weather": {
            "transport": "streamable-http",
            "url": "http://127.0.0.1:8002/mcp",
        },
    }
)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(content="test").send()


@cl.on_message
async def on_message(message: cl.Message):
    # 3️⃣ 取得 tools
    tools = await client.get_tools()
    # 4️⃣ 建立 agent
    agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)
    # 5️⃣ 呼叫 agent
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": message.content}]}
    )

    data = response["messages"][-1].content

    print("data", data)
    print("Response:", response)
    await cl.Message(content=data).send()

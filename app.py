# chainlit
import chainlit as cl

# RAG
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Langchain+MCP
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import create_agent


LLM_MODEL = "qwen3:8b"
SYSTEM_PROMPT = """你是專業的樂園營運決策助手。你的職責是根據天氣狀況和營運手冊提供精確的營運建議。

【工作流程】
1. 接收到用戶詢問後，先分析是否涉及天氣
2. 如涉及天氣，使用 Weather Tool 查詢即時天氣資料
3. 使用 search_knowledge_base 工具查詢營運手冊中的相關規則
4. 根據查詢結果，綜合天氣資料和營運規則，提供明確的決策建議
5. 如需推播通知，調用對應的 LINE Notify 工具
6. 推播成功後 回答已推播的LINE Notify MCP Tool
6.1【回答格式】：已成功推播『晴天/雨天/颱風』通知

【決策規則】
- 晴天：調用 push_sunny_message
- 雨天：調用 push_rainy_message  
- 颱風：調用 push_typhoon_message

【回答格式】
1. 當前天氣狀況（如已查詢）
2. 風險等級
3. 需要關閉的設施（具體列出）
4. 可以開放的設施（具體列出）
5. 營運建議說明
6. 是否需要推播（需人為確認）

【重要原則】
- 所有建議僅供參考，實際執行需經樂園經理確認
- 不得假設工具調用成功，必須等待實際結果
- 回答要精確、專業、有依據
"""

# ========== RAG ==========

file_path = "./樂園營運手冊Ver2.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400, chunk_overlap=150, add_start_index=True
)
texts = text_splitter.split_documents(docs)


embeddings = OllamaEmbeddings(
    model="nomic-embed-text:latest",
)

vector_store = FAISS.from_documents(
    documents=texts,
    embedding=embeddings,
)


@tool
def search_knowledge_base(query: str) -> str:
    """搜索樂園營運手冊知識庫，查詢不同天氣條件下的設施營運規則和決策建議。

    使用時機：
    - 需要了解特定天氣下的營運規則
    - 查詢哪些設施需要關閉或開放
    - 了解風險等級和營運決策說明

    Args:
        query: 搜索問題，例如「晴天的營運規則」、「雨天時哪些設施要關閉」

    Returns:
        相關的營運規則和決策建議，包含設施清單、風險等級、營運說明
    """
    docs = vector_store.similarity_search(query, k=3)

    return "\n\n".join(
        f"【來源 {i+1}】\n{doc.page_content}" for i, doc in enumerate(docs)
    )


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
    welcome_message = """
    **歡迎使用樂園營運決策助手系統**
    我可以協助您：
    A.查詢即時天氣資訊
    B.根據天氣提供設施營運建議
    C.推播營運決策通知（需確認）

    **使用方式：**
    1. 直接詢問天氣狀況 例如：「現在台北的天氣如何？」
    2. 詢問特定天氣的營運規則 例如：「雨天時哪些設施要關閉？」
    3. 請求綜合建議 例如：「根據目前天氣，給我營運建議」
    4. 推播LINE Notify通知

    **重要提醒：**
    所有營運決策建議僅供參考 實際執行需經樂園經理確認。
    """
    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):

    ui_msg = cl.Message(content="")
    await ui_msg.send()

    # 取得 tools
    tools = await client.get_tools()
    tools.append(search_knowledge_base)
    # 建立 agent
    agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)

    # 調用 agent（使用 stream 進行流式輸出）
    async for token, metadata in agent.astream(
        {"messages": [{"role": "user", "content": message.content}]},
        stream_mode="messages",
    ):
        # LLM 文字
        if metadata.get("langgraph_node") == "model":
            await ui_msg.stream_token(token.text)

    await ui_msg.update()

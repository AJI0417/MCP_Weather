import os

# chainlit
import chainlit as cl

# RAG
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Langchain+MCP
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama.chat_models import ChatOllama
from langchain.agents import create_agent


LLM_MODEL = "qwen2.5:7b"
SYSTEM_PROMPT = """
你是專業的樂園營運決策助手。你的職責是根據天氣狀況和營運手冊提供精確的營運建議。
**絕對原則：所有回覆必須使用繁體中文 (zh-tw)，且嚴禁捏造任何工具的查詢結果。必須依賴工具回傳的真實數據。**

【意圖分類與工作流程】
接收到用戶訊息後，請先判斷屬於以下哪種情境，並嚴格執行對應動作：

[情境 A：查詢即時天氣]
- 特徵：用戶詢問「現在天氣」、「今天天氣」、「某地區天氣」等即時狀況。
- 動作：只能調用天氣查詢工具（Weather Tool）。
- 回覆格式：直接回報查詢到的天氣資訊，不需提供營運建議。

[情境 B：查詢營運規則（假設性問題）]
- 特徵：用戶詢問「雨天時...」、「颱風天...」、「哪些設施要關閉」等一般性規則。
- 動作：**絕對不要調用天氣工具**。請直接調用 `search_knowledge_base` 搜尋相關規則。
- 回覆格式：根據手冊內容直接回答，重點列出受影響的設施與規範。若手冊沒寫請誠實告知。

[情境 C：綜合營運決策]
- 特徵：用戶要求「給予目前的營運建議」、「根據現在天氣該怎麼做」。
- 動作：
  1. 先調用天氣查詢工具取得即時天氣。
  2. 根據取得的天氣狀況，調用 `search_knowledge_base` 查詢對應的營運規範。
- 回覆格式：嚴格依照下方【決策報告格式】輸出。

[情境 D：發送推播通知]
- 特徵：用戶明確指示「發送通知」、「推播訊息」。
- 動作：調用 `LINE_Notify` 相關工具發送訊息。
- 回覆格式：必須等待工具執行成功後，僅輸出：「✅ 成功：已成功推播 [通知類型]」。

【決策報告格式】(僅限情境 C 使用)
1. **天氣狀況**：(填入工具實際查詢結果)
2. **設施的營運狀況**：(根據知識庫列出受影響設施)
3. **營運決策與建議**：(說明決策原因與具體建議)
4. **推播建議**：您可以指示我發送『[填入天氣類型]通知』
"""


# ========== RAG ==========
VECTOR_DIR = "./faiss_index"
PDF_file_path = "./樂園營運手冊Ver3.pdf"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

if os.path.exists(VECTOR_DIR):
    print("✅ 載入既有 FAISS index")
    vector_store = FAISS.load_local(
        VECTOR_DIR, embeddings, allow_dangerous_deserialization=True
    )
else:
    print("🆕 首次建立 FAISS index")
    loader = PyPDFLoader(PDF_file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=150,
        add_start_index=True,
    )
    texts = splitter.split_documents(docs)
    vector_store = FAISS.from_documents(texts, embeddings)
    vector_store.save_local(VECTOR_DIR)


@tool
def search_knowledge_base(query: str) -> str:
    """搜索樂園營運手冊知識庫，查詢不同天氣條件下的設施營運規則和決策建議。"""
    docs = vector_store.similarity_search(query, k=5)

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
    C.推播營運決策通知

    **使用方式：**
    1. 直接詢問天氣狀況 例如：「現在的天氣如何？」
    2. 詢問特定天氣的營運規則 例如：「雨天時哪些設施要關閉？」
    3. 請求綜合建議 例如：「根據目前天氣，給我營運建議」
    4. 推播LINE Notify通知
    """
    # 取得 tools
    tools = await client.get_tools()
    tools.append(search_knowledge_base)
    # 建立 agent
    agent = create_agent(model, tools, system_prompt=SYSTEM_PROMPT)

    # 存到 user_session
    cl.user_session.set("agent", agent)
    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):

    agent = cl.user_session.get("agent")

    ui_msg = cl.Message(content="")
    await ui_msg.send()

    # 調用 agent（使用 stream 進行流式輸出）
    async for token, metadata in agent.astream(
        {"messages": [{"role": "user", "content": message.content}]},
        stream_mode="messages",
    ):
        # LLM 文字
        if metadata.get("langgraph_node") == "model":
            await ui_msg.stream_token(token.text)

    await ui_msg.update()

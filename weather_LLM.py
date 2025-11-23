# -*- coding: utf-8 -*-
"""
此檔案使用 LangChain 和 RAG 技術，讓大型語言模型 (LLM) 能夠根據
`weather_data.json` 檔案中的天氣資料來回答使用者的問題。

它會執行以下操作：
1. 從 `weather_data.json` 載入天氣資料。
2. 將天氣資料轉換為 LangChain 的 Document 格式。
3. 使用 OllamaEmbeddings 建立文字向量。
4. 建立一個 FAISS 向量儲存庫作為檢索器 (Retriever)。
5. 設定一個本地 LLM (gemma3:4b) 模型。
6. 建立一個提示模板 (Prompt Template) 來引導 LLM 的回答。
7. 建立一個 RAG 檢索鏈 (Retrieval Chain)。
8. 啟動一個互動式循環，讓使用者可以輸入問題並獲得回答。
"""
# 匯入必要的套件
import chainlit as cl  # 用於建立聊天機器人 UI
import json  # 用於讀取 JSON 檔案
from langchain_ollama import OllamaLLM as Ollama  # 從 langchain_ollama 匯入 Ollama 模型
from langchain_core.prompts import PromptTemplate  # 用於建立提示模板
from langchain_core.documents import Document  # 用於建立文件物件
from langchain_community.vectorstores import FAISS  # 用於建立向量儲存庫
from langchain_ollama import (
    OllamaEmbeddings,
)  # 從 langchain_ollama 匯入 Ollama 嵌入模型
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# 用於建立文件處理鏈
from langchain_classic.chains import create_retrieval_chain  # 用於建立檢索鏈


def create_rag_chain():
    """建立並返回一個 RAG 檢索鏈。"""
    # 1. 載入天氣資料
    try:
        with open("weather_data.json", "r", encoding="utf-8") as f:
            weather_data = json.load(f)  # 從 JSON 檔案載入天氣資料
    except FileNotFoundError:
        print(
            "錯誤：找不到 weather_data.json 檔案。請先執行 Weather_API.py 來生成資料。"
        )
        return None

    # 2. 將資料轉換為 Document 物件
    documents = []
    for entry in weather_data:
        # 將每筆天氣資料轉換為一個字串
        content = f"時間：從 {entry['startTime']} 到 {entry['endTime']}，天氣狀態：{entry['天氣狀態']}，降雨機率：{entry['降雨機率']}，最低溫度：{entry['最低溫度']}，最高溫度：{entry['最高溫度']}，天氣體感：{entry['天氣體感']}。"
        documents.append(Document(page_content=content))  # 建立 Document 物件並加入列表

    # 3. 設定嵌入模型
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text:latest"
    )  # 使用 nomic-embed-text:latest 模型來建立文字向量

    # 4. 建立 FAISS 向量儲存庫
    vector = FAISS.from_documents(
        documents, embeddings
    )  # 使用 FAISS 來建立向量儲存庫，並將文件轉換為向量
    retriever = vector.as_retriever()  # 建立一個檢索器，用於從向量儲存庫中檢索文件

    # 5. 設定 LLM 模型
    llm = Ollama(
        model="gemma3:4b", temperature=0, top_k=5
    )  # 使用 gemma3:4b 模型作為大型語言模型

    # 6. 建立提示模板
    prompt = PromptTemplate.from_template(
        """
        請根據以下天氣資料來回答問題。並且使用遊客中心廣播的口吻來回答
        提醒遊客要根據天氣情況來做應變 比如：天氣熱要多喝水預防中暑 天氣陰暗提醒攜帶雨具
        最後要加上遊客服務中心關心您的字樣來結束
        如果你在資料中找不到答案，請回答「我無法從目前的資料中找到答案」
        請只根據提供的資料使用中文(繁體) 回答，不要添加任何額外的天氣資訊。

        天氣資料：
        {context}

        問題：{input}

        回答："""
    )

    # 7. 建立文件處理鏈和檢索鏈
    document_chain = create_stuff_documents_chain(
        llm, prompt
    )  # 建立一個文件處理鏈，用於將檢索到的文件傳遞給 LLM
    retrieval_chain = create_retrieval_chain(
        retriever, document_chain
    )  # 建立一個檢索鏈，用於整合檢索器和文件處理鏈

    return retrieval_chain  # 返回 RAG 檢索鏈


@cl.on_chat_start
async def on_chat_start():
    """當聊天開始時，這個函式會被呼叫。"""
    rag_chain = create_rag_chain()  # 建立 RAG 檢索鏈
    if rag_chain is None:
        await cl.Message(
            content="錯誤：無法建立 RAG 鏈，請檢查日誌。"
        ).send()  # 如果建立失敗，發送錯誤訊息
        return

    cl.user_session.set("rag_chain", rag_chain)  # 將 RAG 檢索鏈儲存在使用者會話中
    await cl.Message(
        content="天氣問答機器人已準備就緒，請輸入您的問題！"
    ).send()  # 發送歡迎訊息


@cl.on_message
async def on_message(message: cl.Message):
    """當使用者輸入訊息時，這個函式會被呼叫。"""
    rag_chain = cl.user_session.get("rag_chain")  # 從使用者會話中取得 RAG 檢索鏈
    msg = cl.Message(content="")  # 建立一個空的訊息物件，用於串流回答

    if not rag_chain:
        await cl.Message(
            content="錯誤：RAG 鏈未初始化。"
        ).send()  # 如果 RAG 鏈不存在，發送錯誤訊息
        return

    # 使用 astream 方法來串流 RAG 鏈的回答
    async for chunk in rag_chain.astream({"input": message.content}):
        if "answer" in chunk:
            await msg.stream_token(chunk.get("answer"))  # 將每個收到的回答片段串流到 UI
    await msg.update()  # 更新訊息，表示串流結束

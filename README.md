# 樂園營運決策助手

## 專案說明

本專案為一個樂園營運決策的輔助系統，透過整合大型語言模型 (LLM)、檢索增強生成 (RAG) 技術以及外部工具，打造一個可以用自然語言互動的決策助手。

系統能夠根據即時天氣資訊，結合樂園的營運手冊，提供設施開放或關閉的建議，並具備發送 LINE 推播通知的功能。

## 系統架構

本專案採用微服務架構，由以下幾個核心部分組成：

1.  **主應用程式 (`app.py`)**:

    - 使用 **Chainlit** 打造的前端互動介面。
    - 整合 **Langchain** 作為代理 (Agent) 框架，負責解析使用者意圖、調度工具並生成回覆。
    - 運行 **Ollama** 的 `qwen2.5:7b` 模型作為核心 LLM。
    - 透過 `langchain-mcp-adapters` 與 MCP Server 進行通訊。

2.  **知識庫 (RAG)**:

    - 讀取 `樂園營運手冊Ver3.pdf` 作為知識來源。
    - 使用 `HuggingFaceEmbeddings` (`sentence-transformers/all-MiniLM-L6-v2`) 進行文本向量化。
    - 使用 **FAISS** 建立並儲存向量索引，實現快速的語意搜尋。

3.  **MCP Server (`mcp_servers/`)**:
    - **天氣服務 (`weather.py`)**: 運行於 Port `8002`，負責從中央氣象署開放資料平台獲取即時天氣資訊。
    - **LINE 通知服務 (`line_notify.py`)**: 運行於 Port `8001`，負責透過 LINE Messaging API 發送廣播訊息。
    - 這兩個服務使用 `FastMCP` 框架建立，並作為工具提供給主應用的 Langchain Agent 使用。

---

## 操作方法

### 1. 環境設定

- **複製專案**:

  ```bash
  git clone <your-repo-url>
  cd <your-repo-name>
  ```

- **安裝相依套件**:

  - 建議在虛擬環境中安裝。

  ```bash
  pip install -r requirements.txt
  ```

- **設定環境變數**:

  - 在專案根目錄下建立 `.env` 檔案，並填入以下金鑰資訊：

  ```ini
  # weather.py 所需
  Weather_API_KEY="你的中央氣象署 API Key"

  # line_notify.py 所需
  CHANNEL_ACCESS_TOKEN="你的 LINE Channel Access Token"
  ```

- **設定 Ollama**:
  - 請先 [安裝 Ollama](https://ollama.com/)。
  - 下載本專案所需的模型：
    ```bash
    ollama pull qwen2.5:7b
    ```

### 2. 啟動系統

您需要開啟 **三個** 獨立的終端機視窗來分別啟動主應用和兩個 MCP Server。

- **啟動天氣 MCP Server (Terminal 1)**:

  ```bash
  python mcp_servers/weather.py
  ```

- **啟動 LINE 通知 MCP Server (Terminal 2)**:

  ```bash
  python mcp_servers/line_notify.py
  ```

- **啟動主應用程式 (Terminal 3)**:

  - **首次執行**: 第一次啟動時，系統會自動讀取 PDF 並建立 FAISS 索引，請稍待片刻。

  ```bash
  chainlit run app.py
  ```

  啟動後，瀏覽器將會自動打開 `http://localhost:8000` 的聊天介面。

### 3. 使用方式

您可以透過以下幾種方式與決策助手互動：

- **查詢即時天氣**:

  > "現在天氣如何？"

- **查詢營運規則**:

  > "如果下雨天，哪些設施要關閉？"

- **請求綜合建議**:

  > "根據今天的天氣，給我營運建議。"

- **發送推播**:
  > "發送雨天通知"

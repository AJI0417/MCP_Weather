# 🏰 樂園營運決策助手 (Park Operation Decision Assistant)

這是一個基於 **LangChain**、**Ollama (Qwen 3.5)** 與 **MCP (Model Context Protocol)** 架構開發的智慧營運系統。它能結合即時天氣數據與樂園營運手冊（RAG），為管理人員提供精準的設施運行建議，並能一鍵推播通知至 LINE。

---

## ✨ 核心功能

- **🌦️ 即時天氣查詢**：透過氣象署 API 獲取霧峰區（或指定地區）的最新天氣資訊。
- **📖 營運知識檢索 (RAG)**：自動檢索《樂園營運手冊》PDF，回答關於設施雨天限制、安全規範等問題。
- **🤔 綜合營運決策**：AI 自動結合「當前天氣」與「營運規則」，產出專業的營運調整報告。
- **📢 LINE 一鍵推播**：串接 LINE Messaging API，直接將決策結果（如雨天特報、放晴通知）發送給相關人員。

---

## 🛠️ 技術棧

- **前端介面**: Chainlit
- **AI 核心**: Ollama (模型: `qwen3.5:4b`)
- **框架**: LangChain / LangGraph
- **擴充協議**: MCP (Model Context Protocol)
- **向量資料庫**: FAISS (搭配 HuggingFace Embeddings)

---

## 🚀 逐步安裝方法

### 1. 準備環境

確保您的電腦已安裝 **Python 3.12** 以及 [Ollama](https://ollama.com/)。

### 2. 下載模型

在終端機執行以下指令下載 Qwen 3.5 模型：

```bash
ollama pull qwen3.5:4b
```

### 3. 安裝依賴套件

在專案根目錄下執行：

```bash
pip install -r requirements.txt
```

### 4. 設定環境變數

在專案根目錄建立 `.env` 檔案，填入您的 API Key：

```env
# 氣象署 Open Data API Key
Weather_API_KEY=您的_CWA_API_KEY

# LINE Messaging API 設定
CHANNEL_ACCESS_TOKEN=您的_LINE_ACCESS_TOKEN
CHANNEL_SECRET=您的_LINE_SECRET
```

### 5. 準備營運手冊

將您的營運手冊 PDF 命名為 `樂園營運手冊.pdf` 並放在專案根目錄。

---

## 📝 使用方法

本系統需要同時啟動 **MCP 伺服器** 與 **主程式**。

### 第一步：啟動 MCP 伺服器

請開啟兩個終端機，分別啟動天氣服務與 LINE 服務：

- **啟動天氣服務 (Port 8002)**:
  ```bash
  python mcp_servers/weather.py
  ```
- **啟動 LINE 服務 (Port 8001)**:
  ```bash
  python mcp_servers/line_notify.py
  ```

### 第二步：啟動主程式

在第三個終端機啟動對話介面：

```bash
chainlit run app.py
```

### 第三步：開始對話

您可以嘗試輸入以下指令：

- **問天氣**：「現在霧峰區的天氣怎麼樣？」
- **問規則**：「如果下大雨，雲霄飛車可以開嗎？」
- **求建議**：「根據目前天氣，請給我一份營運決策報告。」
- **發通知**：「幫我發送『雨天』天氣通知。」

---

## 📁 專案架構

- `ai/`: 包含 Agent 邏輯、Prompt 與 Tool 定義。
- `mcp_servers/`: 獨立的天氣與 LINE 通知 MCP 服務。
- `rag/`: 處理 PDF 讀取與向量資料庫建立。
- `faiss_index/`: 儲存已建立索引的知識庫。
- `line_api/`: LINE 相關 API 串接邏輯。

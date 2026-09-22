# 主題樂園營運Agent

「主題樂園營運Agent」是一套提供樂園經理使用的營運決策系統。系統會整合中央氣象署天氣資料、設施資料庫與《樂園營運手冊》，產生營運建議；經理明確要求時，也能透過 LINE Messaging API 發送天氣或維修通知。

## 主要功能

- 查詢霧峰區天氣預報、雨量、風速、最大瞬間陣風及颱風警報。
- 查詢 SQLite 資料庫中的設施目前狀態。
- 使用 Markdown 營運手冊與 FAISS 向量索引進行 RAG 檢索。
- 綜合天氣、設施狀態與營運手冊產生營運建議。
- 透過 LINE MCP 發送天氣通知或維修人員通知。
- 提供設施狀態管理、公告管理及 LINE Webhook 的 Flask 介面。

## 模型配置

| 用途           | 模型                    | 執行位置          |
| -------------- | ----------------------- | ----------------- |
| Main Agent     | `gemini-3.8-flash`      | Google Gemini API |
| LINE Sub-agent | `gemma4:e2b`            | 本機 Ollama       |
| RAG Embedding  | `BAAI/bge-base-zh-v1.5` | CPU               |

## 開發與測試環境

- 作業系統：Windows 11
- CPU：Intel Core i5-12600K
- GPU：NVIDIA GeForce RTX 4060 Ti 8 GB
- RAM：32 GB
- Python：3.12

## 系統架構

```text
Chainlit（Main Agent）
├─ Weather MCP（天氣資料）
├─ Facility Status MCP（設施狀態）
├─ RAG（Markdown + FAISS）
└─ LINE Sub-agent
   └─ LINE MCP（遊客通知／維修通知）

Flask Server
├─ 設施狀態管理
├─ 公告管理
└─ LINE Webhook
```

## 安裝方式

以下指令皆使用 Windows CMD，並且必須在專案根目錄執行。

### 1. 安裝必要軟體

請先安裝：

- [Python 3.12](https://www.python.org/downloads/)
- [Ollama for Windows](https://ollama.com/download/windows)
- Git（如需使用 Git 下載專案）

安裝 Python 時，請勾選將 Python 加入 PATH。

### 2. 建立虛擬環境

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

若既有 `.venv` 是從其他路徑搬移而來，或原本的 Python 已被移除，請重新建立虛擬環境。Python 虛擬環境會記錄建立時的 Python 安裝路徑，不能視為可直接搬移的資料夾。

### 3. 準備 Ollama 模型

確認 Ollama 已在背景執行，然後下載 LINE Sub-agent 使用的模型：

```bat
ollama pull gemma4:e2b
```

可使用下列指令確認模型是否存在：

```bat
ollama list
```

若 Ollama 沒有自動啟動，可另外開啟一個 CMD 執行：

```bat
ollama serve
```

### 4. 設定環境變數

在專案根目錄建立 `.env`，內容如下：

```env
# Google Gemini API
GOOGLE_API_KEY=填入_Google_API_Key

# 中央氣象署開放資料平台
Weather_API_KEY=填入_CWA_API_Key

# 發送遊客通知及回覆 LINE Webhook
CHANNEL_ACCESS_TOKEN=填入_LINE_Channel_Access_Token

# 發送維修通知
WORKER_LINE_USER_ID=填入_維修人員_LINE_User_ID
WORKER_CHANNEL_ACCESS_TOKEN=填入_維修頻道_Channel_Access_Token
```

變數名稱有大小寫之分，請保持與範例完全一致。`.env` 已列入 `.gitignore`，請勿將真實金鑰或 Token 提交到版本控制。

### 5. 確認營運手冊

RAG 會直接讀取專案根目錄中的：

```text
樂園營運手冊Ver4.md
```

首次查詢知識庫時，系統會下載 `BAAI/bge-base-zh-v1.5`，並在本機建立 `faiss_index`。Embedding 固定使用 CPU 執行，因此第一次查詢可能需要較長時間。

## 啟動服務

所有服務都要從專案根目錄啟動。請先確認 Ollama 正在執行，再開啟五個 CMD 視窗；每個視窗都要先啟用虛擬環境：

```bat
.venv\Scripts\activate.bat
```

### CMD 1：啟動 LINE MCP（Port 8001）

```bat
python -m mcp_servers.line_notify
```

### CMD 2：啟動 Weather MCP（Port 8002）

```bat
python -m mcp_servers.weather
```

### CMD 3：啟動 Facility Status MCP（Port 8003）

```bat
python -m mcp_servers.get_facility_status
```

### CMD 4：啟動 Flask 管理與 Webhook Server（Port 5000）

```bat
python server.py
```

### CMD 5：啟動 Chainlit（Port 8000）

請先確認三個 MCP Server 均已啟動，再執行：

```bat
python -m chainlit run app.py
```

瀏覽器開啟：

```text
http://127.0.0.1:8000
```

## 服務網址

| 服務                | 網址                                  | 說明                       |
| ------------------- | ------------------------------------- | -------------------------- |
| Chainlit            | `http://127.0.0.1:8000`               | Agent 對話介面             |
| 設施管理            | `http://127.0.0.1:5000/worker`        | 查看及修改設施狀態         |
| 公告列表            | `http://127.0.0.1:5000/announcements` | 查看已發布公告             |
| LINE Webhook        | `http://127.0.0.1:5000/webhook`       | 接收 LINE 事件的 POST 端點 |
| LINE MCP            | `http://127.0.0.1:8001/mcp`           | LINE 通知 MCP 端點         |
| Weather MCP         | `http://127.0.0.1:8002/mcp`           | 天氣 MCP 端點              |
| Facility Status MCP | `http://127.0.0.1:8003/mcp`           | 設施狀態 MCP 端點          |

LINE 平台無法存取電腦上的 `127.0.0.1`。若要接收真實 LINE Webhook，必須透過ngrok提供可從網際網路存取的 HTTPS 網址，並將公開網址的 `/webhook` 設定到 LINE Developers Console。

## 使用範例

- `現在天氣如何？`
- `目前有哪些設施維修中？`
- `如果下大雨，樂園應該怎麼處理？`
- `根據目前狀況提供營運建議。`
- `發送大雨通知。`
- `發送維修通知。`
- `設施狀態如何。`

營運分析只會提出 LINE 通知建議，不會自動推播。只有在經理明確要求「發送」時，Agent 才會呼叫通知工具。

````

## 專案目錄

```text
MCP_Weather\
├─ ai\                    # Main Agent、LINE Sub-agent、Prompt 與工具
├─ db\                    # SQLite 連線、初始化與資料存取
├─ Line_template\         # LINE Flex Message JSON 模板
├─ mcp_client\            # MultiServerMCPClient 設定
├─ mcp_servers\           # LINE、天氣與設施狀態 MCP Server
├─ rag\                   # Markdown 切割、Embedding 與 FAISS
├─ routes\                # Flask 路由
├─ services\              # LINE API 服務
├─ static\                # Flask 靜態檔案
├─ templates\             # Flask HTML 模板
├─ app.py                  # Chainlit 入口
├─ server.py               # Flask 入口
├─ config.py               # 環境變數及共用路徑
├─ requirements.txt        # Python 依賴版本
└─ 樂園營運手冊Ver4.md     # RAG 知識來源
````

## 常見問題

### `ModuleNotFoundError: No module named 'config'`

請確認目前目錄是專案根目錄，並使用模組方式啟動 MCP Server：

```bat
python -m mcp_servers.weather
```

不要先切換到 `mcp_servers` 後執行 `python weather.py`，否則 Python 可能找不到根目錄的 `config.py`。

### Chainlit 啟動或開始對話時顯示連線失敗

Main Agent 在對話開始時會連接三個 MCP Server。請確認 8001、8002、8003 三個服務都已先啟動，且 `mcp_client/mcp_client.py` 中的網址沒有被修改。

### `ollama` 不是內部或外部命令

請安裝 Ollama，重新開啟 CMD，再執行 `ollama --version`。若仍無法使用，請確認 Ollama 已加入系統 PATH。

### Ollama 顯示找不到 `gemma4:e2b`

```bat
ollama pull gemma4:e2b
```

### Google API 回傳 `500 Internal Server Error`

這通常代表 Google Gemini API 的暫時性伺服器錯誤。SDK 會自動重試；如果多次重試後仍失敗，可稍後再試並確認 Google 服務狀態。API Key 無效通常會回傳驗證或權限錯誤，而不是 500。

### 修改營運手冊後仍取得舊內容

`faiss_index` 是由營運手冊建立的本機索引。修改 `樂園營運手冊Ver4.md` 後，需要重新建立索引，才能讓 RAG 使用新版內容。

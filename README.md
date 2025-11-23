# 天氣問答系統

## 專案說明

本專案透過結合中央氣象署的開放天氣資料與大型語言模型 (LLM)，建立一個可以用自然語言互動的天氣問答機器人。

專案包含兩個主要腳本：

1.  **`Weather_API.py`**: 從氣象署 API 獲取臺中市的 36 小時天氣預報，並將其處理後儲存為 `weather_data.json`。
2.  **`Weather_LLM.py`**: 啟動一個搭載 Chainlit UI 的 RAG (Retrieval-Augmented Generation) 問答系統，讓使用者可以根據 `weather_data.json` 的內容進行提問。

---

## 操作方法

### 第一步：獲取天氣資料 (`Weather_API.py`)

此腳本只**需要執行一次** (或在您想更新天氣資料時執行)。

#### 1. 資料來源

-   **API**: [中央氣象署開放資料平台 - 一般天氣預報-今明 36 小時天氣預報](https://opendata.cwa.gov.tw/dataset/forecast/F-C0032-001)

#### 2. 設定

-   **獲取 API 金鑰**:
    -   前往[中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)註冊並登入。
    -   在會員中心找到您的 API 授權碼。
-   **建立 `.env` 檔案**:
    -   在專案根目錄下建立 `.env` 檔案，並填入您的金鑰：
      ```
      API_KEY="在這裡貼上您的API金鑰"
      ```
-   **安裝套件**:
    ```bash
    pip install requests python-dotenv
    ```

#### 3. 執行

```bash
python Weather_API.py
```
執行後，根目錄下會出現 `weather_data.json` 檔案。

---

### 第二步：啟動天氣問答系統 (`Weather_LLM.py`)

#### 1. 功能

-   讀取 `weather_data.json` 的天氣資料。
-   使用 LangChain 和 Ollama 建立 RAG 系統。
-   提供一個 Chainlit 聊天介面，讓您用自然語言查詢天氣。

#### 2. 設定

-   **安裝套件**:
    ```bash
    pip install chainlit langchain langchain-community faiss-cpu langchain-ollama langchain-classic
    ```
    > **注意**: `langchain` 1.0 版更新後，部分模組已移至 `langchain-classic`。此專案已跟隨更新。詳細資訊請參考：[LangChain v1.0 Migration Guide](https://docs.langchain.com/oss/python/migrate/langchain-v1)
-   **安裝並設定 Ollama**:
    -   本專案預設使用 Ollama 來運行本地的大型語言模型。請先[安裝 Ollama](https://ollama.com/)。
    -   安裝完成後，下載本專案所需的模型：
        ```bash
        ollama pull gemma3:4b
        ollama pull nomic-embed-text
        ```
    -   如果您想更換模型，請修改 `Weather_LLM.py` 中的 `llm` 和 `embeddings` 變數。

#### 3. 執行

-   **啟動問答系統**:
    ```bash
    chainlit run Weather_LLM.py -w
    ```
-   此命令會啟動一個本地網頁伺服器，並自動在您的瀏覽器中打開聊天介面。
-   現在，您可以開始在聊天視窗中提問了！

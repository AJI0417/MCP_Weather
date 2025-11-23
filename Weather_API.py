# -*- coding: utf-8 -*-
"""
此檔案從台灣中央氣象署 (CWA) 的開放資料 API 獲取臺中市的天氣資料。
它會檢索三個不同時間段的天氣資訊，處理資料，並將其儲存為 JSON 檔案。
"""
import os
import requests
import json
from dotenv import load_dotenv

# 從 .env 文件加載環境變數
load_dotenv()


def getWeather():
    """獲取並處理臺中市的天氣資料。"""
    # 從環境變數中獲取 API 金鑰
    Weather_API_KEY = os.getenv("API_KEY")
    # 為臺中市建構 API URL
    Weather_API_URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={Weather_API_KEY}&locationName=臺中市"

    # 向 API 發送 GET 請求
    response = requests.get(Weather_API_URL)
    # 解析 JSON 回應
    Weather_data = response.json()

    # 提取地點和天氣元素資料
    location = Weather_data["records"]["location"][0]
    weather_elements = location["weatherElement"]

    # 處理 3 個時間段的資料
    weather_periods = []
    for i in range(3):
        weather_info = {}
        # 為當前時段添加 startTime 和 endTime
        weather_info["startTime"] = weather_elements[0]["time"][i]["startTime"]
        weather_info["endTime"] = weather_elements[0]["time"][i]["endTime"]
        # 提取當前時段每個天氣元素的資料
        for element in weather_elements:
            element_name = element["elementName"]
            time_data = element["time"][i]

            if element_name == "Wx":
                weather_info["天氣狀態"] = time_data["parameter"]["parameterName"]
            elif element_name == "PoP":  # 降水機率
                weather_info["降雨機率"] = time_data["parameter"]["parameterName"] + "%"
            elif element_name == "MinT":  # 最低溫度
                weather_info["最低溫度"] = (
                    time_data["parameter"]["parameterName"] + "°C"
                )
            elif element_name == "MaxT":  # 最高溫度
                weather_info["最高溫度"] = (
                    time_data["parameter"]["parameterName"] + "°C"
                )
            elif element_name == "CI":  # 舒適度指數
                weather_info["天氣體感"] = time_data["parameter"]["parameterName"]
        weather_periods.append(weather_info)

    return weather_periods


def save_to_json(weather_periods, filename="weather_data.json"):
    """將天氣資料儲存到 JSON 檔案。"""
    if not weather_periods:
        print("沒有天氣資訊可以儲存")
        return

    # 將城市名稱添加到每個天氣資料條目中
    for info in weather_periods:
        info["城市"] = "臺中市"

    # 使用 UTF-8 編碼將資料寫入 JSON 檔案
    with open(filename, mode="w", encoding="utf-8") as file:
        # 使用 ensure_ascii=False 以正確處理中文字元
        # 使用 indent=4 進行美化輸出
        json.dump(weather_periods, file, ensure_ascii=False, indent=4)

    print(f"天氣資訊已儲存至 {filename}")


# 主要執行區塊
if __name__ == "__main__":
    # 獲取天氣資料
    weather = getWeather()
    # 將天氣資料列印到控制台
    print(weather)
    # 將天氣資料儲存到 JSON 檔案
    save_to_json(weather, "weather_data.json")

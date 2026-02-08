import requests
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather_MCP_Server", port=8002)
load_dotenv()


@mcp.tool()
def getWeather(LocationName: str = "霧峰區") -> list:
    """
    取得今天霧峰區的天氣預報
    """

    API_Key = os.getenv("Weather_API_KEY")

    # API URL
    API_URL = (
        "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-073"
        f"?Authorization={API_Key}"
        f"&LocationName={LocationName}"
        "&ElementName=天氣預報綜合描述,3小時降雨機率,溫度,天氣現象,體感溫度"
    )

    # 發送請求
    res = requests.get(API_URL)
    data = res.json()

    # 直接定位到 Location
    location_data = data["records"]["Locations"][0]["Location"][0]
    weather_elements = location_data["WeatherElement"]

    # 整理API回傳所有的第一筆資料
    parsed_data = {}
    time_info = {}

    for item in weather_elements:
        element_name = item["ElementName"]

        # 直接取第一筆 (最近的時段)，移除空值檢查
        first_record = item["Time"][0]

        # 直接抓取數值
        val = list(first_record["ElementValue"][0].values())[0]
        parsed_data[element_name] = val

        # 抓取時間區段
        if element_name == "天氣預報綜合描述":
            time_info["StartTime"] = first_record["StartTime"]
            time_info["EndTime"] = first_record["EndTime"]

    # 整理成陣列
    result = {
        "location": LocationName,
        "time": {
            "start": time_info["StartTime"],
            "end": time_info["EndTime"],
        },
        "raw": {
            "溫度": parsed_data["溫度"],
            "體感溫度": parsed_data["體感溫度"],
            "3小時降雨機率": parsed_data["3小時降雨機率"],
            "天氣現象": parsed_data["天氣現象"],
            "天氣預報綜合描述": parsed_data["天氣預報綜合描述"],
        },
    }

    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

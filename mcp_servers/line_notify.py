import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("LINE_Message_Server", port=8001)

# LINE API 設定
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_API_BASE = "https://api.line.me/v2/bot"

# =========== Flex Message 模板配置 ==========
TEMPLATES = {
    "rainy": {
        "altText": "雨天特報",
        "hero_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTxPURVBuFZ5bdIZ-fypFf9-yxKYpgr48OMg&s",
        "title": "喔吼... 勇者們請注意！霧峰區 正降下神祕的洗塵之雨 🌧️",
        "title_color": "#1F1F1F",
        "status_text": "⚠️ 結界微調 (部分開放)",
        "status_color": "#E67E22",
        "body": "雖然雨水洗淨了塵埃，但戶外掃帚飛行可能還是有些危險。老夫已將室內酒館與鍊金室備妥熱茶，請務必披上斗篷，千萬別著涼受寒了，勇者的身體才是冒險的本錢啊！",
    },
    "sunny": {
        "altText": "晴天好天氣",
        "hero_url": "https://images.unsplash.com/photo-1501973801540-537f08ccae7b",
        "title": "☀️ 天氣放晴啦！",
        "title_color": "#1F1F1F",
        "status_text": "✅ 全面開放",
        "status_color": "#27AE60",
        "body": "適合外出、曬棉被、冒險啟程！",
    },
    "typhoon": {
        "altText": "颱風警報",
        "hero_url": "https://images.unsplash.com/photo-1500673922987-e212871fec22",
        "title": "🌪️ 颱風來襲！",
        "title_color": "#D32F2F",
        "status_text": "🚫 全園停園",
        "status_color": "#D32F2F",
        "body": "請避免外出，並做好防颱準備。",
    },
}


def _build_flex_message(template: dict) -> dict:
    """根據模板配置建構 LINE Flex Message"""
    return {
        "type": "flex",
        "altText": template["altText"],
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": template["hero_url"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": template["title"],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                        "color": template["title_color"],
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "地區", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                    {"type": "text", "text": "霧峰區", "wrap": True, "color": "#666666", "size": "sm", "flex": 4},
                                ],
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "狀態", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                    {"type": "text", "text": template["status_text"], "wrap": True, "color": template["status_color"], "size": "lg", "flex": 6, "weight": "bold"},
                                ],
                            },
                        ],
                    },
                    {"type": "separator", "margin": "xl", "color": "#0099FF"},
                    {
                        "type": "text",
                        "text": template["body"],
                        "margin": "lg",
                        "size": "md",
                        "color": "#555555",
                        "wrap": True,
                        "lineSpacing": "4px",
                    },
                ],
            },
        },
    }


# =========== 單一推播工具 ==========
@mcp.tool()
def push_message(weather_type: str) -> dict:
    """推播天氣通知。weather_type: rainy/sunny/typhoon"""


    template = TEMPLATES[weather_type]
    flex_msg = _build_flex_message(template)

    url = f"{LINE_API_BASE}/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {"messages": [flex_msg]}

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": weather_type}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")


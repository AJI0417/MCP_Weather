import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("LINE_Message_Server", port=8001)

# LINE API 設定
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
USER_ID = os.getenv("LINE_USER_ID")
LINE_API_BASE = "https://api.line.me/v2/bot"


# =========== LINE Push Message TOOL ==========
@mcp.tool()
def push_rainy_message():
    """推送【雨天】天氣通知給所有用戶"""
    url = f"{LINE_API_BASE}/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "messages": [
            {
                "type": "flex",
                "altText": "雨天特報",
                "contents": {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTxPURVBuFZ5bdIZ-fypFf9-yxKYpgr48OMg&s",
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
                                "text": f"喔吼... 勇者們請注意！霧峰區 正降下神祕的洗塵之雨 🌧️",
                                "weight": "bold",
                                "size": "lg",
                                "wrap": True,
                                "color": "#1F1F1F",
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
                                            {
                                                "type": "text",
                                                "text": "地區",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 1,
                                            },
                                            {
                                                "type": "text",
                                                "text": "霧峰區",
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 4,
                                            },
                                        ],
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "狀態",
                                                "color": "#aaaaaa",
                                                "size": "sm",
                                                "flex": 1,
                                            },
                                            {
                                                "type": "text",
                                                "text": "⚠️ 結界微調 (部分開放)",
                                                "wrap": True,
                                                "color": "#E67E22",
                                                "size": "lg",
                                                "flex": 6,
                                                "weight": "bold",
                                            },
                                        ],
                                    },
                                ],
                            },
                            {"type": "separator", "margin": "xl", "color": "#0099FF"},
                            {
                                "type": "text",
                                "text": "雖然雨水洗淨了塵埃，但戶外掃帚飛行可能還是有些危險。老夫已將室內酒館與鍊金室備妥熱茶，請務必披上斗篷，千萬別著涼受寒了，勇者的身體才是冒險的本錢啊！",
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
        ]
    }

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": "rainy"}


@mcp.tool()
def push_sunny_message():
    """推送【晴天】天氣通知給所有用戶"""
    url = f"{LINE_API_BASE}/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }

    data = {
        "messages": [
            {
                "type": "flex",
                "altText": "晴天好天氣",
                "contents": {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://images.unsplash.com/photo-1501973801540-537f08ccae7b",
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
                                "text": "☀️ 天氣放晴啦！",
                                "weight": "bold",
                                "size": "xl",
                                "wrap": True,
                            },
                            {
                                "type": "text",
                                "text": "適合外出、曬棉被、冒險啟程！",
                                "margin": "md",
                                "wrap": True,
                            },
                        ],
                    },
                },
            }
        ]
    }

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": "sunny"}


@mcp.tool()
def push_typhoon_message():
    """推送【颱風】警示通知給所有用戶"""
    url = f"{LINE_API_BASE}/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }

    data = {
        "messages": [
            {
                "type": "flex",
                "altText": "颱風警報",
                "contents": {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "url": "https://images.unsplash.com/photo-1500673922987-e212871fec22",
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
                                "text": "🌪️ 颱風來襲！",
                                "weight": "bold",
                                "size": "xl",
                                "color": "#D32F2F",
                            },
                            {
                                "type": "text",
                                "text": "請避免外出，並做好防颱準備。",
                                "margin": "md",
                                "wrap": True,
                            },
                        ],
                    },
                },
            }
        ]
    }

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": "typhoon"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

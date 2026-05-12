import os
import requests
import datetime #new
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("LINE_Message_Server", port=8001)

# LINE API 設定
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
USER_ID = os.getenv("LINE_USER_ID")
LINE_API_BASE = "https://api.line.me/v2/bot"
api_key = os.getenv("_API_KEY")
now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8))) #new



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
                        "url": "https://img.redocn.com/sheji/20220107/wuyunyunduonanguoxiayu_12093067.jpg",
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
                                "text": "🌧 雨天通知",
                                "weight": "bold",
                                "size": "xxl",
                                "align": "center"
                            },
                            {
                                "type": "text",
                                "text": "⚠️親愛的遊客您好：",
                                "wrap": True,
                                "margin": "md",
                                "size": "sm"
                            },
                            {
                                "type": "text",
                                "text": "園區正在受降雨影響,地面較為濕滑,請記得攜帶雨傘且行走時請多加留意安全。⚠️",
                                "wrap": True,
                                "margin": "md",
                                "size": "sm"
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
                                                "text": "地點",
                                                "color": "#000000",
                                                "size": "sm",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": "霧峰遊樂園",
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            },
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "時間",
                                                "color": "#000000",
                                                "size": "sm",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": now.strftime("%Y-%m-%d %H:%M:%S") + f" ({now.tzname()})", #new
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 5
                                            },
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "spacing": "sm",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "關閉設施",
                                                "color": "#000000",
                                                "size": "sm",
                                                "flex": 1
                                            },
                                            {
                                                "type": "text",
                                                "text": "大怒神、G5、摩天輪、室外攤販",
                                                "wrap": True,
                                                "color": "#666666",
                                                "size": "sm",
                                                "flex": 3
                                            },
                                        ]
                                    },
                                ],
                            },
                            {   "type": "separator", 
                                "margin": "xl", 
                                "color": "#0099FF"
                            },
                        ],
                    },
                    "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "link",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "查看資訊",
                                "uri": "https://line.me/"
                            }
                        }
                    ]
                }
                },
            }
        ]
    }

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": "rainy"}


def get_uv_cwa():
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001?Authorization={api_key}"

    try:
        res = requests.get(url)
        data = res.json()

        locations = data["records"]["weatherElement"]["location"]
        uv_list = [float(loc["UVIndex"]) for loc in locations if loc.get("UVIndex") not in (None, "", "-99")]

        if not uv_list:
            return "無資料"

        avg_uv = sum(uv_list) / len(uv_list)

        return round(avg_uv, 1)

    except Exception as e:
        print(e)
        return "無資料"

def uv_level(uvi):
    try:
        uvi = float(uvi)
        if uvi < 3:
            return "低"
        elif uvi < 6:
            return "中"
        elif uvi < 8:
            return "高"
        elif uvi < 11:
            return "強"
        else:
            return "危險"
    except:
        return "未知"

@mcp.tool()
def push_sunny_message():
    """推送【晴天】天氣通知給所有用戶"""
    url = f"{LINE_API_BASE}/message/broadcast"
    uvi = get_uv_cwa()          # ✅ 先抓資料
    level = uv_level(uvi)       # ✅ 再轉等級
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }

    data = {
        "messages": [
            {
            "type": "flex",
            "altText": "晴天通知",
            "contents": {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://image.90sheji.com/tupian/2025/08/16/f2c26f84f51059ca994133a3aac1c7e8.webp?v=20250825&imageMogr2/thumbnail/315x/crop/!x315-0a0/auto-orient/interlace/1/sharpen/1",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": "https://line.me/"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"☀️晴天通知 ",
                            "weight": "bold",
                            "size": "xxl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": f"紫外線:{uvi}（{level}）",
                            "weight": "bold",
                            "size": "md",
                            "align": "start"
                        },
                        {
                            "type": "text",
                            "text": "⚠️親愛的遊客您好： ",
                            "wrap": True,
                            "margin": "md",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": "今天天氣晴朗,適合來點戶外的刺激設施！不過紫外線較強,請記得做好防曬並急時補充水分。 一起享受陽光,留下美好回憶吧！祝你玩得安心又愉快!⚠️",
                            "wrap": True,
                            "margin": "sm",
                            "size": "sm"
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
                                            "text": "地點",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "霧峰遊樂園",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        },
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "時間",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": now.strftime("%Y-%m-%d %H:%M:%S") + f" ({now.tzname()})", #new
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        },
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "關閉設施",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "無",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                    ]
                                },
                            ]
                            
                        },
                        {
                            "type": "separator",
                            "color": "#FF2000",
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "link",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "查看資訊",
                                "uri": "https://line.me/"
                            }
                        }
                    ]
                }
            }
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
            "altText": "颱風天通知",
            "contents": {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://pic.616pic.com/ys_img/01/05/72/x598HGmeYW.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                        "type": "uri",
                        "uri": "https://line.me/"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🌀 颱風天通知",
                            "weight": "bold",
                            "size": "xxl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": "⚠️親愛的遊客您好： ",
                            "wrap": True,
                            "margin": "md",
                            "size": "sm"
                        },
                        {
                            "type": "text",
                            "text": "受颱風影響，為確保您的安全，請務必待在家不要出門!園區即刻起，暫停營運。後續開園時間將依天候狀況另行公告，請持續關注官方最新消息。感謝您的體諒與支持，期待很快再與您相見！ ⚠️",
                            "wrap": True,
                            "margin": "md",
                            "size": "sm"
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
                                            "text": "地點",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "霧峰遊樂園",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        },
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "時間",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": now.strftime("%Y-%m-%d %H:%M:%S") + f" ({now.tzname()})", #new
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        },
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "關閉設施",
                                            "color": "#000000",
                                            "size": "sm",
                                            "flex": 1
                                        },
                                        {
                                            "type": "text",
                                            "text": "舉例",
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                    ]
                                },
                            ]
                            
                        },
                        {
                            "type": "separator",
                            "color": "#B300FF",
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "link",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "查看資訊",
                                "uri": "https://line.me/"
                            }
                        }
                    ]
                }
            }
            }
        ]
    }

    requests.post(url, headers=headers, json=data)
    return {"status": "success", "weather": "typhoon"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

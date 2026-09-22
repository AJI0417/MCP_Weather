import requests

import config


def reply_message(reply_token, flex_content, alt_text):
    """使用 LINE Reply API 傳送 Flex Message。"""
    url = f"{config.LINE_API_BASE}/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "flex",
                "altText": alt_text,
                "contents": flex_content,
            }
        ],
    }

    requests.post(url, headers=headers, json=data)

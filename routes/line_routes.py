import json

from flask import Blueprint, request

import config
from services.line_service import reply_message


line_bp = Blueprint("line", __name__)


def load_flex_messages():
    """讀取存放 Flex Message 的 JSON 檔案。"""
    with open(config.RICH_MENU_FLEX_MESSAGES_PATH, "r", encoding="utf-8") as file:
        flex_data = json.load(file)

    return flex_data


@line_bp.route("/webhook", methods=["POST"])
def webhook():
    """接收 LINE 傳來的文字訊息事件。"""
    flex_data = load_flex_messages()

    body = request.get_json()
    events = body.get("events", [])

    for event in events:
        message = event.get("message", {})
        user_text = message.get("text")
        reply_token = event["replyToken"]

        print(f"實際收到的指令是：[{user_text}]")

        if user_text == "查看今日營運時間":
            reply_message(
                reply_token,
                flex_data["營運時間"],
                "查看今日營運時間",
            )

        elif user_text == "查看最新優惠活動":
            reply_message(
                reply_token,
                flex_data["優惠活動"],
                "查看最新優惠活動",
            )

        elif user_text == "查看樂園資訊":
            reply_message(
                reply_token,
                flex_data["樂園資訊"],
                "查看樂園資訊",
            )

        elif user_text == "查看完整交通資訊":
            reply_message(
                reply_token,
                flex_data["交通資訊"],
                "選擇交通工具",
            )

        elif user_text == "聯絡我們":
            reply_message(
                reply_token,
                flex_data["聯絡資訊"],
                "聯絡客服",
            )

    return "OK", 200

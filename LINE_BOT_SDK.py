from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    LocationMessage, StickerMessage, StickerSendMessage,
    FollowEvent,UnfollowEvent,JoinEvent
)


app = Flask(__name__)

# 設定你的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi('MsAFZ2HPzuQkAfW5vGCQO95+kaoQeLiPQvfmsBowWbj7QPrPw9lXwRI/biAG1gnElDEqhL9SM75WZqUB8EJtmlLK8XocKATD4na7vfCDepfCvgddlwlP0VN19QV44Mr003gERgvZmBaYorQQgfcOYgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0c555055810158eb02bae1f82e4a73a4')

@app.route("/callback", methods=['POST'])
def callback():
    """接收 LINE 的 Webhook 請求"""
    # 取得 X-Line-Signature header 的值
    signature = request.headers['X-Line-Signature']

    # 取得請求的 body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 驗證請求來源
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    print("🤝 有新用戶加入：", user_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="‼️歡迎您的加入‼️我是你的遊樂園小助手有事都可以找我呦😍希望你在樂園玩得開心🌟")
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """處理文字訊息"""
    user_message = event.message.text
    
    # 簡單的回覆邏輯
    if user_message == "你好":
        reply_text = "你好！很高興見到你 😊"
    elif user_message == "功能":
        reply_text = "我可以回覆文字、貼圖，也可以接收圖片、影片等訊息喔！"
    elif user_message == "貼圖":
        # 回覆貼圖
        line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(package_id='446', sticker_id='1988')
        )
        return
    else:
        reply_text = f"你說：{user_message}"
    
    # 回覆訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    user_id = event.source.user_id
    print(f"使用者已經封鎖你了：{user_id}")

@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="大家好～我已經在群組裡面囉！🤖")
    )


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    """處理圖片訊息"""
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="我收到你的圖片了！📷")
    )

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    """處理貼圖訊息"""
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(package_id='446', sticker_id='1989')
    )

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    """處理位置訊息"""
    address = event.message.address
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"收到位置：{address}")
    )

# 主動推送訊息的範例函數
def push_message(user_id, message):
    """主動推送訊息給特定用戶"""
    line_bot_api.push_message(user_id, TextSendMessage(text=message))

# 廣播訊息的範例函數
def broadcast_message(message):
    """廣播訊息給所有好友"""
    line_bot_api.broadcast(TextSendMessage(text=message))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
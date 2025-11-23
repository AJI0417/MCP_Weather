import json
import requests
from flask import Flask, request, abort

app = Flask(__name__)

# LINE API 設定
CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'
LINE_API_BASE = 'https://api.line.me/v2/bot'

# ========== Webhook 接收 ==========
@app.route("/callback", methods=['POST'])
def callback():
    """接收 LINE Platform 的 Webhook Event"""
    # 驗證請求簽章
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    # 這裡應該驗證 signature，範例略過
    
    try:
        events = json.loads(body)['events']
        for event in events:
            handle_event(event)
    except Exception as e:
        print(f"Error: {e}")
        abort(400)
    
    return 'OK'

def handle_event(event):
    """處理各種 Webhook Event"""
    event_type = event['type']
    
    if event_type == 'message':
        handle_message_event(event)
    elif event_type == 'follow':
        handle_follow_event(event)
    elif event_type == 'unfollow':
        handle_unfollow_event(event)
    elif event_type == 'join':
        handle_join_event(event)
    elif event_type == 'postback':
        handle_postback_event(event)

def handle_message_event(event):
    """處理訊息事件"""
    message_type = event['message']['type']
    reply_token = event['replyToken']
    
    if message_type == 'text':
        user_text = event['message']['text']
        
        if user_text == 'Flex':
            reply_flex_message(reply_token)
        elif user_text == 'Quick Reply':
            reply_with_quick_reply(reply_token)
        elif user_text == 'Template':
            reply_template_message(reply_token)
        else:
            reply_text_message(reply_token, f"你說：{user_text}")

def handle_follow_event(event):
    """處理用戶加入好友事件"""
    user_id = event['source']['userId']
    reply_token = event['replyToken']
    reply_text_message(reply_token, "感謝你加入好友！")

def handle_unfollow_event(event):
    """處理用戶封鎖事件"""
    user_id = event['source']['userId']
    print(f"User {user_id} unfollowed")

def handle_join_event(event):
    """處理 Bot 加入群組/聊天室事件"""
    reply_token = event['replyToken']
    reply_text_message(reply_token, "大家好！很高興加入這個群組")

def handle_postback_event(event):
    """處理 Postback 事件（按鈕點擊）"""
    data = event['postback']['data']
    reply_token = event['replyToken']
    reply_text_message(reply_token, f"你選擇了：{data}")

# ========== 回覆訊息 API ==========
def reply_text_message(reply_token, text):
    """Reply Message API - 回覆文字訊息"""
    url = f"{LINE_API_BASE}/message/reply"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'text',
                'text': text
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

def reply_with_quick_reply(reply_token):
    """回覆帶有 Quick Reply 的訊息"""
    url = f"{LINE_API_BASE}/message/reply"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'text',
                'text': '請選擇一個選項：',
                'quickReply': {
                    'items': [
                        {
                            'type': 'action',
                            'action': {
                                'type': 'message',
                                'label': '選項 A',
                                'text': '我選擇 A'
                            }
                        },
                        {
                            'type': 'action',
                            'action': {
                                'type': 'message',
                                'label': '選項 B',
                                'text': '我選擇 B'
                            }
                        },
                        {
                            'type': 'action',
                            'action': {
                                'type': 'location',
                                'label': '傳送位置'
                            }
                        }
                    ]
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

def reply_template_message(reply_token):
    """回覆 Template Message (Buttons Template)"""
    url = f"{LINE_API_BASE}/message/reply"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'template',
                'altText': '這是按鈕模板',
                'template': {
                    'type': 'buttons',
                    'thumbnailImageUrl': 'https://via.placeholder.com/1024x1024',
                    'title': '選單標題',
                    'text': '請選擇功能',
                    'actions': [
                        {
                            'type': 'postback',
                            'label': '功能 1',
                            'data': 'action=function1'
                        },
                        {
                            'type': 'postback',
                            'label': '功能 2',
                            'data': 'action=function2'
                        },
                        {
                            'type': 'uri',
                            'label': '查看網站',
                            'uri': 'https://line.me'
                        }
                    ]
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

def reply_flex_message(reply_token):
    """回覆 Flex Message"""
    url = f"{LINE_API_BASE}/message/reply"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [
            {
                'type': 'flex',
                'altText': 'Flex Message',
                'contents': {
                    'type': 'bubble',
                    'hero': {
                        'type': 'image',
                        'url': 'https://via.placeholder.com/1024x768',
                        'size': 'full',
                        'aspectRatio': '20:13',
                        'aspectMode': 'cover'
                    },
                    'body': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': [
                            {
                                'type': 'text',
                                'text': 'Flex Message 範例',
                                'weight': 'bold',
                                'size': 'xl'
                            },
                            {
                                'type': 'text',
                                'text': '這是一個彈性訊息示範',
                                'size': 'sm',
                                'color': '#999999',
                                'margin': 'md'
                            }
                        ]
                    },
                    'footer': {
                        'type': 'box',
                        'layout': 'vertical',
                        'contents': [
                            {
                                'type': 'button',
                                'action': {
                                    'type': 'uri',
                                    'label': '了解更多',
                                    'uri': 'https://developers.line.biz'
                                },
                                'style': 'primary'
                            }
                        ]
                    }
                }
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

# ========== Push Message API ==========
def push_message(user_id, text):
    """Push Message API - 主動推送訊息"""
    url = f"{LINE_API_BASE}/message/push"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': user_id,
        'messages': [
            {
                'type': 'text',
                'text': text
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ========== Multicast Message API ==========
def multicast_message(user_ids, text):
    """Multicast Message API - 發送給多個用戶"""
    url = f"{LINE_API_BASE}/message/multicast"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': user_ids,  # 最多 500 個 user IDs
        'messages': [
            {
                'type': 'text',
                'text': text
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ========== Broadcast Message API ==========
def broadcast_message(text):
    """Broadcast Message API - 廣播給所有好友"""
    url = f"{LINE_API_BASE}/message/broadcast"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'messages': [
            {
                'type': 'text',
                'text': text
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# ========== 取得用戶資料 API ==========
def get_profile(user_id):
    """取得用戶個人資料"""
    url = f"{LINE_API_BASE}/profile/{user_id}"
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# ========== Rich Menu API ==========
def create_rich_menu():
    """建立 Rich Menu"""
    url = f"{LINE_API_BASE}/richmenu"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'size': {
            'width': 2500,
            'height': 1686
        },
        'selected': True,
        'name': 'Rich Menu 1',
        'chatBarText': '點擊查看選單',
        'areas': [
            {
                'bounds': {
                    'x': 0,
                    'y': 0,
                    'width': 1250,
                    'height': 1686
                },
                'action': {
                    'type': 'message',
                    'text': '左側按鈕'
                }
            },
            {
                'bounds': {
                    'x': 1250,
                    'y': 0,
                    'width': 1250,
                    'height': 1686
                },
                'action': {
                    'type': 'message',
                    'text': '右側按鈕'
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def link_rich_menu_to_user(user_id, rich_menu_id):
    """將 Rich Menu 綁定到用戶"""
    url = f"{LINE_API_BASE}/user/{user_id}/richmenu/{rich_menu_id}"
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    response = requests.post(url, headers=headers)
    return response.status_code == 200

# ========== 取得訊息配額 ==========
def get_quota():
    """取得本月可發送訊息數上限"""
    url = f"{LINE_API_BASE}/message/quota"
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_consumption():
    """取得本月已發送訊息數"""
    url = f"{LINE_API_BASE}/message/quota/consumption"
    headers = {
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(port=5000, debug=True)
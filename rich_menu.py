import requests

# LINE API 設定
CHANNEL_ACCESS_TOKEN = 'u14qjM/JgUvgcw3NzPfQWQ1YsLapa5HB1bKodkUT3Q5712bdxpxtBaKj5E7DY+0SAWarxAeJtcOjaMDaI/HTPzvmYc18od/FyX/II+qrBBfdzOkPlsHeEToCKC3fVwvg5InpVaNKBmj+gPfHbVPwqQdB04t89/1O/w1cDnyilFU='
LINE_API_BASE = 'https://api.line.me/v2/bot'
LINE_IMAGE_BASE = 'https://api-data.line.me/v2/bot/richmenu'

def create_rich_menuA():
    """建立 Rich Menu A"""
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
        'selected': False,
        'name': 'Rich Menu A',
        'chatBarText': '測試A',
        'areas': [
            {
                'bounds': {
                    'x': 0,
                    'y': 0,
                    'width': 1250,
                    'height': 1686
                },
                'action': {
                    'type': 'uri',
                    'uri': 'https://developers.line.biz/'
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
                    'type': 'richmenuswitch',
                    'richMenuAliasId': 'richmenu-alias-b',
                    'data': 'richmenu-changed-to-b',
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["richMenuId"]


def create_rich_menuB():
    """建立 Rich Menu B"""
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
        'selected': False,
        'name': 'Rich Menu B',
        'chatBarText': '測試B',
        'areas': [
            {
                'bounds': {
                    'x': 0,
                    'y': 0,
                    'width': 1250,
                    'height': 1686
                },
                'action': {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-a",
                    "data": "richmenu-changed-to-a"
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
                    "type": "uri",
                    "uri": "https://lineapiusecase.com/en/top.html"
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["richMenuId"]

def create_alias(alias_id, richmenu_id):
    url = f"{LINE_API_BASE}/richmenu/alias"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        "richMenuAliasId": alias_id,
        "richMenuId": richmenu_id
    }
    return requests.post(url, headers=headers, json=data)

def upload_menu_image(richmenu_id,image_path):
    url = f"{LINE_IMAGE_BASE}/{richmenu_id}/content"
    headers = {
        'Content-Type': 'image/png',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    with open(image_path, "rb") as f:
        return requests.post(url, headers=headers, data=f)

def set_default(richmenu_id):
    url = f"https://api.line.me/v2/bot/user/all/richmenu/{richmenu_id}"
    headers = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    requests.post(url, headers=headers)

def delete_menu_image(richmenu_id):
    url = f"{LINE_IMAGE_BASE}/{richmenu_id}/content"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    return requests.delete(url, headers=headers)


if __name__ == "__main__":
    richmenu_a = create_rich_menuA()
    richmenu_b = create_rich_menuB()


    delete_menu_image(richmenu_a)
    res_c = upload_menu_image(richmenu_a, "./images/B.png")
    print(f"C:{res_c.status_code, res_c.text}")

    delete_menu_image(richmenu_b)
    res_d = upload_menu_image(richmenu_b, "./images/d.png")
    print(f"D:{res_d.status_code, res_d.text}")

    create_alias("richmenu-alias-a", richmenu_a)
    create_alias("richmenu-alias-b", richmenu_b)

    set_default(richmenu_a)
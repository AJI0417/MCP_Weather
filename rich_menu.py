import requests
import os
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
LINE_API_BASE = "https://api.line.me/v2/bot"
LINE_IMAGE_BASE = "https://api-data.line.me/v2/bot/richmenu"


def clean_all_richmenus():
    """清理所有舊的 rich menu 和 alias"""
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}

    # 清除預設 rich menu
    response = requests.delete(f"{LINE_API_BASE}/user/all/richmenu", headers=headers)
    print(f"清除預設: {response.status_code}")

    # 刪除 aliases
    for alias in ["richmenu-alias-a", "richmenu-alias-b"]:
        response = requests.delete(
            f"{LINE_API_BASE}/richmenu/alias/{alias}", headers=headers
        )
        print(f"刪除alias{alias}: {response.status_code}")

    # 3. 取得並刪除所有 rich menu
    print("取得所有 rich menu...")
    response = requests.get(f"{LINE_API_BASE}/richmenu/list", headers=headers)
    richmenus = response.json().get("richmenus", [])
    for menu in richmenus:
        menu_id = menu["richMenuId"]
        print(f"刪除 rich menu: {menu_id}")
        response = requests.delete(
            f"{LINE_API_BASE}/richmenu/{menu_id}", headers=headers
        )
        print(f"狀態: {response.status_code}")


def create_rich_menuA():
    """建立 Rich Menu A"""
    url = f"{LINE_API_BASE}/richmenu"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "size": {"width": 2500, "height": 1686},
        "selected": False,
        "name": "Rich Menu A",
        "chatBarText": "測試A",
        "areas": [
            {
                "bounds": {"x": 0, "y": 835, "width": 1662, "height": 851},
                "action": {"type": "message", "text": "測試頁面A"},
            },
            {
                "bounds": {"x": 0, "y": 0, "width": 846, "height": 842},
                "action": {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-b",
                    "data": "richmenu-changed-to-b",
                },
            },
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"建立 Rich Menu A: {response.json()['richMenuId']}")
    return response.json()["richMenuId"]


def create_rich_menuB():
    """建立 Rich Menu B"""
    url = f"{LINE_API_BASE}/richmenu"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "size": {"width": 2500, "height": 1686},
        "selected": False,
        "name": "Rich Menu B",
        "chatBarText": "測試B",
        "areas": [
            {
                "bounds": {"x": 1836, "y": 0, "width": 660, "height": 796},
                "action": {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-a",
                    "data": "richmenu-changed-to-a",
                },
            },
            {
                "bounds": {"x": 4, "y": 842, "width": 660, "height": 557},
                "action": {
                    "type": "message",
                    "text": "測試頁面B",
                },
            },
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"建立 Rich Menu B: {response.json()['richMenuId']}")
    return response.json()["richMenuId"]


def create_alias(alias_id, richmenu_id):
    url = f"{LINE_API_BASE}/richmenu/alias"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {"richMenuAliasId": alias_id, "richMenuId": richmenu_id}
    response = requests.post(url, headers=headers, json=data)
    print(f"建立 alias {alias_id}: {response.status_code}")
    return response


def upload_menu_image(richmenu_id, image_path):
    url = f"{LINE_IMAGE_BASE}/{richmenu_id}/content"
    headers = {
        "Content-Type": "image/png",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    with open(image_path, "rb") as f:
        response = requests.post(url, headers=headers, data=f)
        print(f"上傳圖片 {image_path}: {response.status_code}")
        return response


def set_default(richmenu_id):
    url = f"https://api.line.me/v2/bot/user/all/richmenu/{richmenu_id}"
    headers = {"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    response = requests.post(url, headers=headers)
    print(f"設定預設 rich menu: {response.status_code}")
    return response


if __name__ == "__main__":
    # 清理所有舊的 rich menu
    clean_all_richmenus()

    # 建立新的 rich menu
    richmenu_a = create_rich_menuA()
    richmenu_b = create_rich_menuB()

    # 上傳圖片
    upload_menu_image(richmenu_a, "./images/A.png")
    upload_menu_image(richmenu_b, "./images/B.png")

    # 建立 aliases
    create_alias("richmenu-alias-a", richmenu_a)
    create_alias("richmenu-alias-b", richmenu_b)

    # 設定預設
    set_default(richmenu_a)

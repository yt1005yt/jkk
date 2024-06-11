import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz

URL = "https://jkkwatcher.com/recentupdate/"
LINE_TOKEN = "3cy6RmlkDHAwwTKxf47aGbBrkahjd4w0r6sLobN5cN7"
JST = pytz.timezone('Asia/Tokyo')

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching page content: {e}")
        notify_via_line(f"Error fetching page content: {e}")
        return ""

def parse_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    properties = []
    for item in soup.select('tr'):  # Adjusted to select rows from the table
        columns = item.find_all('td')
        if len(columns) >= 6:  # Ensure there are enough columns
            name = columns[1].text.strip()  # Property name
            type_ = columns[2].text.strip()  # Property type
            category = columns[3].text.strip()  # Property category
            properties.append((name, type_, category))
    return properties

def has_page_changed(current_properties, previous_properties):
    return current_properties != previous_properties

def notify_via_line(message):
    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {
            "Authorization": f"Bearer {LINE_TOKEN}"
        }
        data = {
            "message": message
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"LINE通知ステータスコード: {response.status_code}")
        print(f"LINE通知レスポンス: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending LINE notification: {e}")

previous_properties = []

while True:
    try:
        current_content = get_page_content(URL)
        if not current_content:
            time.sleep(600)  # Retry after 10 minutes if error occurs
            continue

        print("ページ内容を取得しました。")
        current_properties = parse_content(current_content)
        print(f"取得した物件数: {len(current_properties)}")

        if has_page_changed(current_properties, previous_properties):
            print("ページが更新されました。")
            changes = len(current_properties) - len(previous_properties)
            update_time = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')
            message = f"物件情報が更新されました。\n更新日時: {update_time}\n変更数: {changes}\n\n"
            for prop in current_properties:
                message += f"物件名: {prop[0]}, タイプ: {prop[1]}, 種別: {prop[2]}\n"
            notify_via_line(message)
            print("LINE通知を送りました。")

            previous_properties = current_properties
        else:
            print("ページは更新されていません。")

        # 現在時刻を日本時間で取得
        current_time = datetime.now(JST).time()
        if current_time >= datetime.strptime('08:00', '%H:%M').time() and current_time <= datetime.strptime('21:00', '%H:%M').time():
            # 朝8時から夜9時の間は10分ごとに実行
            time.sleep(600)  # 600秒 = 10分
        else:
            # 夜9時から朝7時の間は1時間ごとに実行
            time.sleep(3600)  # 3600秒 = 1時間

    except Exception as e:
        print(f"An error occurred: {e}")
        notify_via_line(f"An error occurred: {e}")
        time.sleep(600)  # Retry after 10 minutes if error occurs

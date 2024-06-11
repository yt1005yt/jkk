import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

URL = "https://jkkwatcher.com/recentupdate/"
LINE_TOKEN = "3cy6RmlkDHAwwTKxf47aGbBrkahjd4w0r6sLobN5cN7"

def get_page_content(url):
    response = requests.get(url)
    return response.text

def parse_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    properties = []
    for item in soup.select('.property-item'):  # Adjust the selector based on actual HTML structure
        name = item.select_one('.property-name').text.strip()
        type_ = item.select_one('.property-type').text.strip()
        category = item.select_one('.property-category').text.strip()
        properties.append((name, type_, category))
    return properties

def has_page_changed(current_properties, previous_properties):
    return current_properties != previous_properties

def notify_via_line(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "message": message
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)

previous_properties = []

while True:
    current_content = get_page_content(URL)
    current_properties = parse_content(current_content)
    
    if has_page_changed(current_properties, previous_properties):
        changes = len(current_properties) - len(previous_properties)
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"物件情報が更新されました。\n更新日時: {update_time}\n変更数: {changes}\n\n"
        for prop in current_properties:
            message += f"物件名: {prop[0]}, タイプ: {prop[1]}, 種別: {prop[2]}\n"
        notify_via_line(message)
        
        previous_properties = current_properties
    
    # Wait for a specified time interval before checking again (e.g., 60 seconds)
    time.sleep(60)

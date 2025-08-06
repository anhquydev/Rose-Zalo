import os
import requests
from zlapi.models import *
from config import ADMIN

ADMIN_ID = ADMIN

des = {
    'version': "1.0.0",
    'credits': "Nguyễn Đức Tài",
    'description': "Tạo file theo yêu cầu",
    'power': "Quản trị viên Bot"
}

def is_admin(author_id):
    return author_id in ADMIN_ID

def create_mock_link(code_content, file_name):
    try:
        data = {
            "status": 200,
            "content": code_content,
            "content_type": "text/plain",
            "charset": "UTF-8",
            "secret": "Kaito Kid",
            "expiration": "never"
        }
        response = requests.post("https://api.mocky.io/api/mock", json=data)
        response_data = response.json()
        return response_data.get("link"), None
    except Exception as e:
        return None, str(e)

def handle_crtf_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        return

    parts = message.split('|', 1)
    if len(parts) != 2:
        return

    file_name_part, file_content = parts
    file_name = file_name_part.strip().split(" ", 1)[-1].lstrip(",.") 
    file_content = file_content.strip()

    if not file_name:
        return

    mock_url, error = create_mock_link(file_content, file_name)
    if error:
        return

    extension = file_name.split(".")[-1].upper()

    client.sendRemoteFile(
        fileUrl=mock_url,
        fileName=file_name,
        thread_id=thread_id,
        thread_type=thread_type,
        fileSize=None,
        extension=extension
    )
    
def ft_vxkiue():
    return {
        'createfile': handle_crtf_command
    }

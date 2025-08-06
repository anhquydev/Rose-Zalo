from zlapi.models import *
import os
import json
import requests
from PIL import Image
from io import BytesIO

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "làm nét ảnh",
    'power': "Thành viên"
}

def get_image_dimensions(url, headers):
    image_response = requests.get(url, headers=headers)
    image = Image.open(BytesIO(image_response.content))
    width, height = image.size
    return width, height

def handle_4k_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if message_object.quote:
            client.replyMessage(Message(text="@Member, Đợi Chút\nWaiting For Me 10-60 seconds !", mention=Mention(author_id, length=len("@Member"), offset=0)), message_object, thread_id, thread_type, ttl=7)
            msgrep = message_object.quote
            attach_str = msgrep['attach']
            attach_data = json.loads(attach_str)
            picture = attach_data['href']
            converted_url = picture.replace("\\", "")
            api_url = f'https://www.hungdev.id.vn/ai/4k?url={converted_url}&apikey=817e64bd0a'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            response = requests.get(api_url, headers=headers)
            response.raise_for_status()

            data = response.json()
            image_url = data['data']

            image_response = requests.get(image_url, headers=headers)
            image_path = 'temp_image.jpg'

            with open(image_path, 'wb') as f:
                f.write(image_response.content)

            width, height = get_image_dimensions(image_url, headers)
            client.sendLocalImage(
                image_path,
                thread_id=thread_id,
                thread_type=thread_type,
                width=width,
                height=height,
                ttl=86400000
            )
            os.remove(image_path)

        else:
            client.replyMessage(Message(text="@Member, reply hình ảnh cần làm nét đi !", mention=Mention(author_id, length=len("@Member"), offset=0)), message_object, thread_id, thread_type, ttl=5000)
            return
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def ft_vxkiue():
    return {
        '4k': handle_4k_command
    }
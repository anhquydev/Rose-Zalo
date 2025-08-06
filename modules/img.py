from zlapi.models import Message, Mention
import time
import random
import os
import requests
import urllib.parse
import uuid
from PIL import Image
from io import BytesIO

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Tìm ảnh Pin (random 1)",
    'power': "Thành viên"
}

def handle_img_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 2 or not text[1].strip():
        error_message = Message(text="• Vui lòng nhập nội dung cần tìm ảnh.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    search_terms = " ".join(text[1:])
    encoded_text = urllib.parse.quote(search_terms, safe='')

    try:
        apianh = f'https://api.sumiproject.net/pinterest?search={encoded_text}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }

        response = requests.get(apianh, headers=headers)
        response.raise_for_status()
        data = response.json()
        links = data.get('data', [])

        if not links:
            error_message = Message(text="Không tìm thấy ảnh nào!")
            client.sendMessage(error_message, thread_id, thread_type)
            return

        random_link = random.choice(links)
        if random_link:
            image_response = requests.get(random_link, headers=headers)
            image_response.raise_for_status()
            
            try:
                image_content = BytesIO(image_response.content)
                img = Image.open(image_content)
                width, height = img.size
            except Exception as e:
                error_message = Message(text=f"Không thể xử lý hình ảnh: {str(e)}")
                client.sendMessage(error_message, thread_id, thread_type)
                return


            image_name = f"{uuid.uuid4()}.jpeg"
            image_path = os.path.join(os.getcwd(), image_name)

            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            
            mention_text = f"[@{author_id}]"
            message_text = f"{mention_text} [{search_terms}]"
            
            client.sendLocalImage(
                    imagePath=image_path,
                    message=Message(
                        text=message_text,
                        mention=Mention(author_id, length=len(f"@{author_id}"), offset=1)
                    ),
                    thread_id=thread_id,
                    thread_type=thread_type,
                    width=width,
                    height=height,
                    ttl=200000
                )
            os.remove(image_path)

        else:
            error_message = Message(text="Không thể lấy link ảnh.")
            client.sendMessage(error_message, thread_id, thread_type)
            return

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except KeyError as e:
        error_message = Message(text=f"Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def ft_vxkiue():
    return {
        'img': handle_img_command
    }
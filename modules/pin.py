import time
from zlapi.models import *
import requests
import urllib.parse
import os

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Tìm ảnh Pin",
    'power': "Thành viên"
}

def handle_pin_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 2 or not text[1].strip():
        error_message = Message(text="Thưa Sếp, vui lòng nhập nội dung cần tìm ảnh. ✅")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
        return

    search_terms = " ".join(text[1:])
    encoded_text = urllib.parse.quote(search_terms, safe='')

    try:
        apianh = f'https://api.sumiproject.net/pinterest?search={encoded_text}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(apianh, headers=headers)
        response.raise_for_status()

        data = response.json()
        links = data.get('data', [])

        if not links:
            error_message = Message(text="Không tìm thấy ảnh nào. 🚫")
            client.sendMessage(error_message, thread_id, thread_type)
            client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
            return

        image_paths = []
        for idx, link in enumerate(links):
            if link:
                image_response = requests.get(link, headers=headers)
                image_path = f'modules/cache/temp_image_{idx}.jpeg'
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                image_paths.append(image_path)

        if all(os.path.exists(path) for path in image_paths):
            total_images = len(image_paths)
            gui = Message(text=f"Đã gửi {total_images} ảnh tìm kiếm từ Pinterest. ✅")
            client.sendMultiLocalImage(
                imagePathList=image_paths,
                message=gui,
                thread_id=thread_id,
                thread_type=thread_type,
                width=1600,
                height=1600,
                ttl=200000
            )
            client.sendReaction(message_object, "✅", thread_id, thread_type, reactionType=75)
            for path in image_paths:
                os.remove(path)

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"❌ Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
        client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
    except KeyError as e:
        error_message = Message(text=f"❌ Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
        client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
    except Exception as e:
        error_message = Message(text=f"❌ Đã xảy ra lỗi không xác định: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
        client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)

def ft_vxkiue():
    return {
        'pin': handle_pin_command
    }

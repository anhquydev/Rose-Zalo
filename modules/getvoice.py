import json
import requests
import urllib.parse
import subprocess
from zlapi.models import Message
import os

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Lấy audio từ video và gửi lên nhóm",
    'power': "Thành viên"
}
last_sent_image_url = None


def extract_audio(video_url, output_file):
    try:
        command = ["ffmpeg", "-y", "-i", video_url, "-vn", "-acodec", "aac", "-b:a", "128k", output_file]
        subprocess.run(command, check=True)
        return True
    except Exception as e:
        print(f"Lỗi khi trích xuất âm thanh: {e}")
        return False

def upload_to_uguu(file_name):
    try:
        with open(file_name, 'rb') as file:
            files = {'files[]': file}
            response = requests.post('https://uguu.se/upload', files=files).json()
            if response['success']:
                return response['files'][0]['url']
            return False
    except Exception as e:
        print(f"Error in upload_to_uguu: {e}")
        return False

def handle_getvoice_command(message, message_object, thread_id, thread_type, author_id, client):
    global last_sent_image_url
    msg_obj = message_object
    video_url = None

    if msg_obj.msgType == "chat.video.msg":
        img_url = msg_obj.content.href.replace("\\/", "/")
        video_url = urllib.parse.unquote(img_url)
    elif msg_obj.quote:
        attach = msg_obj.quote.attach
        if attach:
            try:
                attach_data = json.loads(attach)
                video_url = attach_data.get('hdUrl') or attach_data.get('href')
            except json.JSONDecodeError as e:
                print(f"Lỗi khi phân tích JSON: {e}")
                return

    if video_url:
        output_file = "src.aac"
        if os.path.exists(output_file):
            os.remove(output_file)
        if extract_audio(video_url, output_file):
            audio_url = upload_to_uguu(output_file)
            if audio_url:
                client.sendRemoteVoice(audio_url, thread_id, thread_type, fileSize=1)
                client.replyMessage(Message(text="Rét doi của bạn đây"), message_object, thread_id, thread_type)
            else:
                client.replyMessage(Message(text="Lỗi khi upload lên host"), message_object, thread_id, thread_type)
        else:
            client.replyMessage(Message(text="Cái này có phải video đâu mà get"), message_object, thread_id, thread_type)
    else:
        client.replyMessage(Message(text="Vui lòng reply vào video để lấy audio."), message_object, thread_id, thread_type)


def ft_vxkiue():
    return {
        'getvoice': handle_getvoice_command
    }
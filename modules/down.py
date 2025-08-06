import requests
from zlapi.models import Message
import ffmpeg
import json
import io
import os

des = {
    'version': "1.1.0",
    'credits': "Vũ Xuân Kiên",
    'description': "Tải video từ TikTok, YouTube, Facebook, CapCut và Douyin và gửi về nhóm chat",
    'power': "Thành viên"
}

def get_video_info(video_url):
    try:
        probe = ffmpeg.probe(video_url)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream:
            duration = float(video_stream['duration']) * 1000
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            return duration, width, height
        else:
            raise Exception("Không tìm thấy luồng video trong URL")
    except Exception as e:
        raise Exception(f"Lỗi khi lấy thông tin video: {str(e)}")

def upload_to_imgur(buffered):
    api_url = "https://api.imgur.com/3/image"
    headers = {
        "Authorization": f"Client-ID 85a847235508ec9"
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            files={'image': buffered}
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('link')
        else:
            return None
    except Exception as e:
        return None

def handle_video_download(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()
    if len(content) < 2:
        client.replyMessage(Message(text="Vui lòng nhập một đường link hợp lệ."), message_object, thread_id, thread_type, ttl=60000)
        return
    
    video_link = content[1].strip()
    send_audio = False
    if len(content) > 2 and content[2].lower() == "audio":
        send_audio = True

    if not video_link.startswith("https://"):
        client.replyMessage(Message(text="Vui lòng nhập một đường link hợp lệ (bắt đầu bằng https://)."), message_object, thread_id, thread_type, ttl=60000)
        return
    
    api_map = {
        "https://vt.tiktok.com/": "tiktok",
        "https://www.tiktok.com/": "tiktok",
        "https://www.youtube.com/": "youtube",
        "https://youtu.be/": "youtube",
        "https://www.facebook.com/": "fb",
        "https://www.capcut.com/": "capcut",
        "https://v.douyin.com/": "douyin"
    }
    
    for prefix, api_type in api_map.items():
        if video_link.startswith(prefix):
            if api_type == "tiktok":
                api_url = f'https://niio-team.onrender.com/downr?url={video_link}'
            if api_type == "youtube":
                 api_url = f'https://niio-team.onrender.com/downr?url={video_link}'
            if api_type == "douyin":
                 api_url = f'https://niio-team.onrender.com/downr?url={video_link}'
            else:
                api_url = f'https://niio-team.onrender.com/downr?url={video_link}'
            try:
                response = requests.get(api_url)
                response.raise_for_status()
                data = response.json()
                
                video_url = None
                title = None
                thumbnail_url = None
                if api_type == "tiktok":
                    if 'medias' not in data or not data['medias']:
                        raise ValueError("Không thể lấy video từ TikTok")

                    video_url = None
    # Ưu tiên link không watermark
                    for media in data['medias']:
                     if media.get("quality") == "no_watermark":
                         video_url = media.get("url")
                         break
                    if not video_url:
                        video_url = data['medias'][0]['url']

                    title = data.get('title', 'Không có tiêu đề')
                    thumbnail_url = data.get('thumbnail')
                    duration = data.get('duration', 0)
                    view = None  # Không có sẵn trong API hiện tại
                    like = None
                    down = None
                    cmt = None
                    share = None
                    title = data.get('title', 'Không có tiêu đề')
                    thumbnail_url = data.get('thumbnail')
                    duration = int(data.get('duration', 0))  # đã tính sẵn là ms
                    author = data.get('author', 'Không rõ')
                    unique_id = data.get('unique_id', 'Không rõ')
                    user_info = client.fetchUserInfo(author_id)
                    user_name = user_info.changed_profiles[author_id].zaloName

                    video_info = (
                        f"[ {user_name} ]\n\n"
                        f"• 🎬 Nền Tảng: TikTok\n"
                        f"• 🔍 Tên : {author}\n"
                        f"• 🔎 Id TikTok : {unique_id}\n"
                        f"• 💻 Tiêu đề: {title}\n\n"
                        f"• 📎 Bot By Anh Quý"
                    )
                    messagesend = Message(text=video_info)
                if api_type == "youtube":
                    if 'medias' not in data or not data['medias']:
                        raise ValueError("Không thể lấy video từ YouTube")

                    video_url = None
    # Ưu tiên video mp4 (360p, 720p...)
                    for media in data['medias']:
                     if media.get("quality", "").startswith("mp4"):
                         video_url = media.get("url")
                         break

                    if not video_url:
                        video_url = data['medias'][0]['url']

                    title = data.get('title', 'Không có tiêu đề')
                    thumbnail_url = data.get('thumbnail')
                    duration = int(data.get('duration', 0)) * 1000  # giây → mili giây
                    author = data.get('author', 'Không rõ')
                    unique_id = data.get('unique_id', 'Không rõ')

                    user_info = client.fetchUserInfo(author_id)
                    user_name = user_info.changed_profiles[author_id].zaloName

                    video_info = (
                        f"[ {user_name} ]\n\n"
                        f"• 🎬 Nền Tảng: YouTube\n"
                        f"• 💻 Tiêu đề: {title}\n\n"
                        f"• 📎 Bot By Anh Quý"
                    )
                    messagesend = Message(text=video_info)

                if video_url:
                    try:
# Gửi trực tiếp video_url luôn, không cần Imgur
                            video_duration = duration
                            client.sendRemoteVideo(
                                video_url,
                                thumbnail_url,
                                duration=video_duration,
                                message=messagesend,
                                thread_id=thread_id,
                                thread_type=thread_type,
                                ttl=86400000,
                                width=720,
                                height=1280
                            )

                    except Exception as e:
                        client.replyMessage(Message(text=f"Lỗi khi lấy thông tin video: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)
                        return
                else:
                    client.replyMessage(Message(text="Không thể lấy được link video."), message_object, thread_id, thread_type, ttl=60000)
                
                return

            except requests.exceptions.RequestException as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)
                return
            except ValueError as e:
                client.replyMessage(Message(text=str(e)), message_object, thread_id, thread_type, ttl=60000)
                return 
            except Exception as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)
                return

def ft_vxkiue():
    return {
        'download': handle_video_download
    }
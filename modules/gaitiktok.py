import requests
from zlapi.models import Message
import ffmpeg

des = {
    'version': "1.1.0",
    'credits': "Vũ Xuân Kiên",
    'description': "xem gái tiktok những lúc nứng",
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

def i4_video(video_url, message_object, thread_id, thread_type, author_id, client, message_text=None):
    try:
        thumbnail_url = 'https://f54-zpg-r.zdn.vn/jpg/1593082208972721683/63c52b8ec1697b372278.jpg'
        messagesend = Message(text=message_text) if message_text else None

        video_info = get_video_info(video_url)
        if video_info:
            video_duration, video_width, video_height = video_info
        else:
            video_duration, video_width, video_height = 2000, 1200, 1600

        client.sendRemoteVideo(
                video_url,
                thumbnail_url,
                duration=video_duration,
                message=messagesend,
                thread_id=thread_id,
                thread_type=thread_type,
                ttl=86400000,
                width=video_width,
                height=video_height
        )
    except Exception as e:
        client.replyMessage(Message(text=f"Lỗi khi gửi video: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)
        return

def handle_gaitiktok(message, message_object, thread_id, thread_type, author_id, client):
    try:
        api_url = 'https://subhatde.id.vn/random/tiktok'
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        author_name = data['author']['name']
        author_username = data['author']['username']
        stats = data['stats']
        views = stats.get('views', 'N/A')
        likes = stats.get('likes', 'N/A')
        comments = stats.get('comments', 'N/A')
        shares = stats.get('shares', 'N/A')
        collects = stats.get('collects', 'N/A')
        video_url = data['attachments'][0]['url']
        user_info = client.fetchUserInfo(author_id)
        user_name = user_info.changed_profiles[author_id].zaloName
        message_text = (
            f"• [ {user_name} ]\n\n"
            f"👤 Author: {author_name} [@{author_username}]\n"
            f"📊 Lượt Xem: {views}\n"
            f"⚕️ Lượt Like: {likes}\n"
            f"📮 Số Bình Luận: {comments}\n"
            f"📉 Lượt Chia Sẻ: {shares}\n"
            f"💜 Lượt Yêu Thích: {collects}"
        )
        i4_video(video_url, message_object, thread_id, thread_type, author_id, client, message_text)
        
    except requests.exceptions.RequestException as e:
        client.replyMessage(Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)
    except Exception as e:
        client.replyMessage(Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}"), message_object, thread_id, thread_type, ttl=60000)

def ft_vxkiue():
    return {
        'gaitiktok': handle_gaitiktok
    }
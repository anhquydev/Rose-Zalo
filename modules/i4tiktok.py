import requests
import urllib.parse
from zlapi.models import Message, MultiMsgStyle, MessageStyle

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Kiểm tra thông tin TikTok User",
    'power': "Thành viên"
}

def handle_checkhost_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()
    if len(content) < 2:
        error_message = "Vui lòng nhập tên người dùng TikTok để kiểm tra thông tin."
        client.replyMessage(
            Message(
                text=error_message, 
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_message), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len(error_message), style="bold", auto_format=False)
                ])
            ), message_object, thread_id, thread_type
        )
        return

    username = " ".join(content[1:]).strip()  # Lấy tên người dùng TikTok từ thông điệp
    try:
        encoded_query = urllib.parse.quote(username)
        api_url = f'https://api.sumiproject.net/tiktok?info={encoded_query}'  # Sửa URL API cho đúng
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        print("Dữ liệu nhận được từ API:", data)

        if data.get("code") != 0:  # Kiểm tra trạng thái trả về từ API
            raise KeyError("Không có thông tin nào được tìm thấy cho người dùng này.")
        
        user_data = data.get("data", {}).get("user", {})
        stats_data = data.get("data", {}).get("stats", {})

        nickname = user_data.get("nickname", "N/A")
        unique_id = user_data.get("uniqueId", "N/A")
        avatar = user_data.get("avatarThumb", "N/A")
        signature = user_data.get("signature", "N/A")
        verified = user_data.get("verified", False)
        bio_email = user_data.get("bio_email", "N/A")
        
        following_count = stats_data.get("followingCount", 0)
        follower_count = stats_data.get("followerCount", 0)
        heart_count = stats_data.get("heartCount", 0)
        video_count = stats_data.get("videoCount", 0)

        result = (
            f"Thông tin người dùng TikTok: {nickname} (@{unique_id})\n\n"
            f"Avatar: {avatar}\n"
            f"Tiểu sử: {signature}\n"
            f"Đã xác minh: {'Có' if verified else 'Không'}\n"
            f"Email: {bio_email}\n\n"
            f"Thông tin thống kê:\n"
            f"Số người theo dõi: {follower_count}\n"
            f"Số người đang theo dõi: {following_count}\n"
            f"Số lượt thích: {heart_count}\n"
            f"Số video: {video_count}"
        )

        client.replyMessage(
            Message(
                text=result, 
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len(result), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len(result), style="bold", auto_format=False)
                ])
            ), message_object, thread_id, thread_type
        )

    except requests.exceptions.RequestException as e:
        error_message = f"Đã xảy ra lỗi khi gọi API: {str(e)}"
        client.replyMessage(
            Message(
                text=error_message, 
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_message), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len(error_message), style="bold", auto_format=False)
                ])
            ), message_object, thread_id, thread_type
        )
    except KeyError as e:
        error_message = f"Lỗi: {str(e)}"
        client.replyMessage(
            Message(
                text=error_message, 
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_message), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len(error_message), style="bold", auto_format=False)
                ])
            ), message_object, thread_id, thread_type
        )
    except Exception as e:
        error_message = f"Đã xảy ra lỗi không xác định: {str(e)}"
        client.replyMessage(
            Message(
                text=error_message, 
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len(error_message), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len(error_message), style="bold", auto_format=False)
                ])
            ), message_object, thread_id, thread_type
        )

def ft_vxkiue():
    return {
        'i4tiktok': handle_checkhost_command
    }

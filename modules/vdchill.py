from zlapi.models import Message
import requests
import random
import json
import ffmpeg

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Gửi video chill",
    'power': "Thành viên"
}

def get_video_info(video_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            probe = ffmpeg.probe(video_url)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if not video_stream:
                 raise ValueError("Không tìm thấy luồng video trong URL")

            duration = float(video_stream['duration']) * 1000
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            return duration, width, height
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video (lần {attempt + 1}/{max_retries}): {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Đợi {wait_time} giây trước khi thử lại...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Không thể lấy thông tin video sau nhiều lần thử: {str(e)}") from e

def handle_vdchill_command(message, message_object, thread_id, thread_type, author_id, client):    
    try:
        with open("modules/cache/data/vdchill.json", "r") as video_file:
            video_urls = json.load(video_file)
        
        video_url = random.choice(video_urls)
        image_url = "https://"
        duration, width, height = get_video_info(video_url)

        client.sendRemoteVideo(
            video_url, 
            image_url,
            duration=int(duration),
            message=None,
            thread_id=thread_id,
            thread_type=thread_type,
            width=width,
            height=height
        )

    except requests.exceptions.RequestException as e:
        error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)
    except Exception as e:
        error_message = Message(text=f"Đã xảy ra lỗi: {str(e)}")
        client.sendMessage(error_message, thread_id, thread_type)

def ft_vxkiue():
    return {
        'vdchill': handle_vdchill_command
    }

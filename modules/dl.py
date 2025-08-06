import re
import os
import requests
from zlapi.models import Message
from bs4 import BeautifulSoup
import json
import ffmpeg
from PIL import Image
import io


des = {
    'version': "1.0.9",
    'credits': "Nguyễn Đức Tài",
    'description': "Tải video hoặc ảnh từ link (capcut, tiktok, youtube, facebook, douyin, pinterest, ig,...)",
    'power': "siuuu"
}

def key():
    with open('seting.json', 'r') as f:
        return json.load(f).get('key')

def get_video_info(video_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            probe = ffmpeg.probe(video_url)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if not video_stream:
                raise Exception("Không tìm thấy luồng video trong URL")

            duration = float(video_stream['duration']) * 1000
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            return duration, width, height


        except Exception as e:
            if attempt < max_retries - 1:
              continue
            else:
                raise Exception(f"Lỗi khi lấy thông tin video: {e}")

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

def handle_down_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip()
    video_link = message_object.href if message_object.href else None

    def extract_links(content):
        urls = re.findall(r'(https?://[^\s]+)', content)
        soup = BeautifulSoup(content, "html.parser")
        href_links = [a['href'] for a in soup.find_all('a', href=True)]
        return urls + href_links

    if not video_link:
        links = extract_links(content)
        if not links:
            error_message = Message(text="Vui lòng nhập một đường link cần down hợp lệ.")
            client.replyMessage(error_message, message_object, thread_id, thread_type)
            return
        video_link = links[0].strip()

    def downall(video_link):
        try:
            api_url = f'https://hungdev.id.vn/medias/down-aio?url={video_link}&apikey=41733ef6c6'
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            
            if data.get('success') and data.get('data'):
                medias = data['data'].get('medias', [])
                tit = data['data'].get('title', 'Không có tiêu đề')
                dang = data['data'].get('source', 'Không có nguồn')

                image_links = []
                video_url = None
                audio_url = None


                for media in medias:
                    media_type = media.get('type')
                    if media_type == 'image':
                        image_links.append(media.get('url'))
                    elif media_type == 'video':
                        quality = media.get('quality')
                        desired_qualities = ['360p', 'no_watermark', 'SD', 'No Watermark', 'Full HD']
                        if quality in desired_qualities:
                            video_url = media.get('url')
                    elif media_type == 'audio':
                         audio_url = media.get('url')
                return image_links, video_url, audio_url, tit, dang

        except requests.exceptions.RequestException as e:
            raise Exception(f"Đã xảy ra lỗi khi gọi API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Dữ liệu từ API không đúng cấu trúc: {str(e)}")
        except Exception as e:
            raise Exception(f"Đã xảy ra lỗi không xác định: {str(e)}")

    try:
        image_urls, video_url, audio_url, tit, dang = downall(video_link)
        sendtitle = f"🎬 Nền tảng: {dang}\n💻 Tiêu đề: {tit}"
        headers = {'User-Agent': 'Mozilla/5.0'}

        if image_urls:
            image_paths = []
            for index, image_url in enumerate(image_urls):
                image_response = requests.get(image_url, headers=headers)
                image_path = f'modules/cache/{index + 1}.jpeg'
                
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                
                image_paths.append(image_path)

            if all(os.path.exists(image_path) for image_path in image_paths):
                message_to_send = Message(text=sendtitle)
                
                
                image_widths = []
                image_heights = []

                for image_path in image_paths:
                    with Image.open(image_path) as img:
                        width, height = img.size
                        image_widths.append(width)
                        image_heights.append(height)
                        
                avg_width = int(sum(image_widths) / len(image_widths))
                avg_height = int(sum(image_heights) / len(image_heights))
                

                client.sendMultiLocalImage(
                    imagePathList=image_paths,
                    thread_id=thread_id,
                    thread_type=thread_type,
                    width=avg_width,
                    height=avg_height
                )
                for image_path in image_paths:
                    os.remove(image_path)
            else:
                raise Exception("Không có ảnh")
            
        if audio_url:
            try:
                audio_response = requests.get(audio_url, headers=headers)
                audio_path = 'modules/cache/audio.mp3'
                with open(audio_path, 'wb') as f:
                    f.write(audio_response.content)
                
                aac_file = audio_path.replace(".mp3", ".aac")
                os.rename(audio_path, aac_file)
                
                uguu_url = upload_to_uguu(aac_file)
                
                if uguu_url:
                    messagesend = Message(text=f"{sendtitle}\n\n🎧 Audio: {uguu_url}")
                    client.sendMessage(messagesend, thread_id, thread_type)
                    client.sendRemoteVoice(uguu_url, thread_id, thread_type, fileSize=1)
                    os.remove(aac_file) 
                else:
                    raise Exception("Không thể tải lên uguu.se")
            except Exception as e:
                raise Exception(f"Lỗi khi xử lý audio: {e}")
                
        elif video_url:
            messagesend = Message(text=sendtitle)
            thumbnailUrl = 'https://f59-zpg-r.zdn.vn/jpg/3574552058519415218/d156abc8a66e1f30467f.jpg'

            try:
                duration, width, height = get_video_info(video_url)
            except Exception as e:
                 duration = '99999999999999999999'
                 width = 1200
                 height = 1600

            client.sendRemoteVideo(
                video_url, 
                thumbnailUrl,
                duration=duration,
                thread_id=thread_id,
                thread_type=thread_type,
                width=width,
                height=height
            )

        else:
             
            error_message = Message(text="Không tìm thấy video, ảnh hoặc audio với yêu cầu.")
            client.sendMessage(error_message, thread_id, thread_type)
    
    except Exception as e:
        error_message = Message(text=str(e))
        client.sendMessage(error_message, thread_id, thread_type)

def ft_vxkiue():
    return {
        'dl': handle_down_command
    }
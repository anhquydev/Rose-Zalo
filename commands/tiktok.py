import requests
import urllib.parse
from zlapi.models import Message
from logging_utils import Logging
logger = Logging()
class TiktokHandler:
    def __init__(self, client):
        self.client = client
    def handle_tiktok_command(self, message, message_object, thread_id, thread_type, author_id):
        content = message.strip().split()
        if len(content) < 2:
            error_message = "Nhập từ khóa tìm kiếm video TikTok đi bạn!"
            self.client.replyMessage(
                Message(
                    text=error_message,
                ), message_object, thread_id, thread_type, ttl=12000
            )
            return
        keyword = " ".join(content[1:]).strip()
        try:
            encoded_keyword = urllib.parse.quote(keyword)
            api_url = f'https://api.sumiproject.net/tiktok?search={encoded_keyword}'
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            print("Dữ liệu nhận được từ API:", data)
            if not data or 'data' not in data or 'videos' not in data['data']:
                raise KeyError("Không có video nào được tìm thấy cho từ khóa này.")
            videos = data['data']['videos']
            if len(videos) == 0:
                error_message = "Không tìm thấy video TikTok nào với từ khóa bạn yêu cầu."
                self.client.replyMessage(
                    Message(
                        text=error_message,
                    ), message_object, thread_id, thread_type, ttl=12000
                )
                return
            gui = f"📍Chọn số thứ tự video để tải:\n\n"
            if thread_id not in self.client.search_results:
              self.client.search_results[thread_id] = {}
            self.client.search_results[thread_id][author_id] = videos
            for i, video in enumerate(videos):
                title = video.get('title', 'No title')
                views = video.get('play_count', 0)
                likes = video.get('digg_count', 0)
                share = video.get('share_count', 0)
                down = video.get('download_count', 0)
                cmt = video.get('comment_count', 0)
                gui += (f"{i+1}. Title: {title}\n📊: {views} | 💜: {likes} | 📮: {cmt} | 📽️ : {share} | 📥: {down}\n\n")
            messagesend = Message(
                text=gui,
            )
            response_message = self.client.replyMessage(messagesend, message_object, thread_id, thread_type, ttl=self.client.search_result_ttl*1000)
            if thread_id not in self.client.search_result_messages:
               self.client.search_result_messages[thread_id] = {}
            self.client.search_result_messages[thread_id][author_id] = {
                 'message': response_message,
                 'time': self.client.get_current_time()
            }
        except requests.exceptions.RequestException as e:
            error_message = f"{str(e)}"
            self.client.replyMessage(
                Message(
                    text=error_message,
                ), message_object, thread_id, thread_type, ttl=12000
            )
        except KeyError as e:
            error_message = f"{str(e)}"
            self.client.replyMessage(
                Message(
                    text=error_message,
                ), message_object, thread_id, thread_type, ttl=12000
            )
        except TypeError as e:
            error_message = f"{str(e)}"
            self.client.replyMessage(
                Message(
                    text=error_message,
                ), message_object, thread_id, thread_type, ttl=12000
            )
        except Exception as e:
            error_message = f"{str(e)}"
            self.client.replyMessage(
                Message(
                    text=error_message,
                ), message_object, thread_id, thread_type, ttl=12000
            )
from zlapi.models import Message
import requests
from bs4 import BeautifulSoup
import os
from fake_useragent import UserAgent
import random
import re
import time
import json  # Import thư viện json

des = {
    'version': "1.3.0",
    'credits': "Vũ Xuân Kiên",
    'description': "Tìm kiếm nhạc trên Zing MP3",
    'power': "Thành viên"
}

def handle_zingmp3_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()

    if len(content) < 2:
        error_message = Message(text="Nhập tên bài hát bạn muốn tìm kiếm trên Zing MP3.")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=20000)
        return

    tenbaihat = ' '.join(content[1:])

    def search_zingmp3(query):
        try:
            base_url = "https://zingmp3.vn"
            search_url = f"{base_url}/tim-kiem/tat-ca?q={requests.utils.quote(query)}"

            messagesend = Message(text="Đang tìm kiếm...")
            client.replyMessage(messagesend, message_object, thread_id, thread_type)

            response = requests.get(search_url)  # No need for specific headers for Zing MP3
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            song_items = soup.find_all('div', class_='section-song')  # Adjust selector if needed

            song_list = []
            for item in song_items:
                try:
                    title_element = item.find('a', class_='title-item')
                    artist_element = item.find('a', class_='singer-item')
                    link_element = item.find('a')  # Find any <a> tag within the item
                    img_element = item.find('img')

                    title = title_element.text.strip() if title_element else "Không tìm thấy tiêu đề"
                    artist = artist_element.text.strip() if artist_element else "Không tìm thấy nghệ sĩ"
                    link = base_url + link_element['href'] if link_element and link_element.has_attr('href') else "Không tìm thấy link"
                    image = img_element['src'] if img_element and img_element.has_attr('src') else ""

                    song_list.append({"title": title, "artist": artist, "link": link, "image": image})

                except Exception as e:
                    print(f"Lỗi khi xử lý một mục bài hát: {e}")

            return song_list

        except requests.exceptions.RequestException as e:
            print(f"Lỗi yêu cầu: {e}")
            return None
        except Exception as e:
            print(f"Lỗi chung: {e}")
            return None

    if tenbaihat:
        results = search_zingmp3(tenbaihat)

        if results:
            message_text = "Kết quả tìm kiếm Zing MP3:\n"
            for i, song in enumerate(results[:5]):  # Limit to first 5 results
                message_text += f"{i+1}. {song['title']} - {song['artist']}\n"
                message_text += f"   Link: {song['link']}\n"
                message_text += "\n"

            messagesend = Message(text=message_text)
            client.replyMessage(messagesend, message_object, thread_id, thread_type, ttl=3600000)


        else:
            messagesend = Message(text="Không tìm thấy bài hát nào phù hợp.")
            client.replyMessage(messagesend, message_object, thread_id, thread_type, ttl=3600000)
    else:
        messagesend = Message(text="Vui lòng nhập tên bài hát.")
        client.replyMessage(messagesend, message_object, thread_id, thread_type, ttl=3600000)

def ft_vxkiue():
    return {
        'zingmp3': handle_zingmp3_command # Changed the command name here
    }
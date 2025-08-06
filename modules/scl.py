from zlapi.models import Message
import requests
from bs4 import BeautifulSoup
import os
from fake_useragent import UserAgent
import random
import re
import time

des = {
    'version': "1.3.0",
    'credits': "Vũ Xuân Kiên",
    'description': "A trai gay sex",
    'power': "Thành viên"
}

def handle_scl_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message.strip().split()

    if len(content) < 2:
        error_message = Message(text="Nhập tên bài hát")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=20000)
        return

    tenbaihat = ' '.join(content[1:])

    def get_client_id():
        client_id_file = 'client_id.txt'
        if os.path.exists(client_id_file):
            with open(client_id_file, 'r') as file:
                client_id = file.read().strip()
                if client_id:
                    return client_id

        try:
            res = requests.get('https://soundcloud.com/', headers=get_headers())
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            script_tags = soup.find_all('script', {'crossorigin': True})
            urls = [tag.get('src') for tag in script_tags if tag.get('src') and tag.get('src').startswith('https')]
            if not urls:
                raise Exception('Không tìm thấy URL script')

            res = requests.get(urls[-1], headers=get_headers())
            res.raise_for_status()
            client_id = res.text.split(',client_id:"')[1].split('"')[0]

            with open(client_id_file, 'w') as file:
                file.write(client_id)

            return client_id
        except Exception as e:
            print(f"Không thể lấy client ID: {e}")
            error_message = Message(text="Không thể lấy client ID. Vui lòng thử lại.")
            client.sendMessage(error_message, thread_id, thread_type)
            return None

    def wait_for_client_id():
        while True:
            client_id = get_client_id()
            if client_id:
                return client_id
            print("Đang chờ client ID...")
            time.sleep(5)

    def get_headers():
        user_agent = UserAgent()
        headers = {
            "User-Agent": user_agent.random,
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "fr-FR,fr;q=0.9",
                "es-ES,es;q=0.9",
                "de-DE,de;q=0.9",
                "zh-CN,zh;q=0.9"
            ]),
            "Referer": 'https://soundcloud.com/',
            "Upgrade-Insecure-Requests": "1"
        }
        return headers

    def search_song(query):
        try:
            link_url = 'https://soundcloud.com'
            headers = get_headers()
            search_url = f'https://m.soundcloud.com/search?q={requests.utils.quote(query)}'
            messagesend = Message(text="Đợi bố tí")
            client.replyMessage(messagesend, message_object, thread_id, thread_type)
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            url_pattern = re.compile(r'^/[^/]+/[^/]+$')
            for element in soup.select('div > ul > li > div'):
                a_tag = element.select_one('a')
                if a_tag and a_tag.has_attr('href'):
                    relative_url = a_tag['href']
                    if url_pattern.match(relative_url):
                        title = a_tag.get('aria-label', '')
                        url = link_url + relative_url
                        img_tag = element.select_one('img')
                        if img_tag and img_tag.has_attr('src'):
                            cover_url = img_tag['src']
                        else:
                            cover_url = None

                        return url, title, cover_url
            return None, None, None
        except Exception as e:
            print(f"Lỗi khi tìm kiếm bài hát: {e}")
            return None, None, None

    def download(link):
        try:
            client_id = wait_for_client_id()
            if not client_id:
                return None
            headers = get_headers()
            api_url = f'https://api-v2.soundcloud.com/resolve?url={link}&client_id={client_id}'
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            progressive_url = next((t['url'] for t in data.get('media', {}).get('transcodings', []) if t['format']['protocol'] == 'progressive'), None)
            if not progressive_url:
                raise Exception('Không tìm thấy URL âm thanh')
            response = requests.get(f'{progressive_url}?client_id={client_id}&track_authorization={data.get("track_authorization")}', headers=headers)
            response.raise_for_status()
            url = response.json().get('url')
            return url
        except Exception as e:
            print(f"Lỗi khi tải âm thanh: {e}")
            return None

    def save_file_to_cache(url, filename):
        try:
            response = requests.get(url, headers=get_headers(), stream=True)
            response.raise_for_status()
            cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            file_path = os.path.join(cache_dir, filename)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            if os.path.getsize(file_path) == 0:
                print(f"Tệp {file_path} có kích thước bằng 0. Xóa tệp.")
                os.remove(file_path)
                return None

            print(f"Tải file thành công! Đã lưu tại {file_path}")
            return file_path
        except Exception as e:
            print(f"Lỗi khi tải file: {e}")
            return None

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

    def delete_file(file_path):
        try:
            os.remove(file_path)
            print(f"Đã xóa tệp: {file_path}")
        except Exception as e:
            print(f"Lỗi khi xóa tệp: {e}")

    if tenbaihat:
        print(f"Tên bài hát tìm thấy: {tenbaihat}")
        link, title, cover = search_song(tenbaihat)
        if link:
            print(f"URL bài hát tìm thấy: {link}")
            mp3_file = save_file_to_cache(download(link), 'downloaded_file.mp3')

            if mp3_file:
                aac_file = mp3_file.replace(".mp3", ".aac")
                try:
                    os.rename(mp3_file, aac_file)
                except Exception as rename_error:
                     print(f"Rename error: {rename_error}")
                     delete_file(mp3_file)
                     return
                upload_response = upload_to_uguu(aac_file)

                if upload_response:
                    try:
                        cover_response = requests.get(cover)
                        open(cover.rsplit("/", 1)[-1], "wb").write(cover_response.content)
                    except:
                        pass

                    messagesend = Message(text=f"• Music Name: {title}\n• Detail: {link}")
                    [
                        client.replyMessage(messagesend, message_object, thread_id, thread_type,ttl=3600000)
                    ]
                    client.sendRemoteVoice(voiceUrl=upload_response, thread_id=thread_id, thread_type=thread_type, ttl=3600000)

                    delete_file(aac_file)
                    try:
                        delete_file(cover.rsplit("/", 1)[-1])
                    except:
                        pass

                else:
                    print("Không thể tải lên Uguu.se.")
                    delete_file(aac_file)
            else:
                print("Không thể tải file âm thanh.")
        else:
            print("Không tìm thấy bài hát.")
    else:
        print("Tên bài hát không được bỏ trống.")


def ft_vxkiue():
    return {
        'scl': handle_scl_command
    }
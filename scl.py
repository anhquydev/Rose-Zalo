import requests
from bs4 import BeautifulSoup
import os
from fake_useragent import UserAgent
import random
import re
import time

CATBOX_PHPSESSID = "ce9f3eddc250f6a5008ccadcd"
APIKEY = "ce9f3eddc250f6a5008ccadcd"

def handle_scl_command(tenbaihat):

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
            print("Không thể lấy client ID. Vui lòng thử lại.")
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
            print("Đang tìm kiếm...")
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            url_pattern = re.compile(r'^/[^/]+/[^/]+$')

            results = []
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
                        results.append({"url": url, "title": title, "cover_url": cover_url})
            return results
        except Exception as e:
            print(f"Lỗi khi tìm kiếm bài hát: {e}")
            return []

    def download(link, filename):
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
            audio_url = response.json().get('url')
            cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
            os.makedirs(cache_dir, exist_ok=True)
            file_path = os.path.join(cache_dir, filename)

            response = requests.get(audio_url, stream=True, headers=get_headers())
            response.raise_for_status()

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"Tải file thành công! Đã lưu tại {file_path}")
            return file_path

        except Exception as e:
            print(f"Lỗi khi tải âm thanh: {e}")
            return None

    def upload_to_catbox(media_url):
        headers = {
            'authority': 'catbox.moe',
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-AU;q=0.6,en;q=0.5,fr-FR;q=0.4,fr;q=0.3,en-US;q=0.2',
            'origin': 'https://catbox.moe',
            'referer': 'https://catbox.moe/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Chromium";v="112"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 12; SM-A037F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        }
        try:
            with open(media_url, 'rb') as f:
              files = {'fileToUpload': f}
              data = {'reqtype': 'fileupload', 'userhash': APIKEY}

              response = requests.post('https://catbox.moe/user/api.php', cookies={'PHPSESSID':CATBOX_PHPSESSID}, headers=headers, data=data, files=files)


            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"Lỗi API Catbox: {response.status_code} - {response.text}")
                return None
        except requests.RequestException as e:
            print(f"Lỗi khi gọi API Catbox: {str(e)}")
            return None
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file để upload.")
            return None

    def delete_file(file_path):
        try:
            os.remove(file_path)
            print(f"Đã xóa tệp: {file_path}")
        except Exception as e:
            print(f"Lỗi khi xóa tệp: {e}")

    if tenbaihat:
        print(f"Tên bài hát tìm thấy: {tenbaihat}")
        results = search_song(tenbaihat)

        if results:
            message_text = "Kết quả tìm kiếm:\n"
            for i, result in enumerate(results):
                message_text += f"{i+1}. {result['title']}\n"
            message_text += "\nNhập số thứ tự bài hát bạn muốn tải (hoặc 'hủy'):"
            print(message_text)

            user_choice = input("Nhập lựa chọn của bạn: ")

            if user_choice.lower() == "hủy":
                print("Đã hủy yêu cầu.")
                return

            try:
                choice_index = int(user_choice) - 1
                if 0 <= choice_index < len(results):
                    selected_song = results[choice_index]
                    song_url = selected_song['url']
                    song_title = selected_song['title']
                    aac_filename = f"{song_title}.aac"

                    print(f"Đang tải và xử lý: {song_title}")

                    aac_file = download(song_url, aac_filename)

                    if aac_file:
                        catbox_url = upload_to_catbox(aac_file)

                        if catbox_url:
                            print(f"Tải hoàn thành:\nTiêu đề: {song_title}\nCatbox URL: {catbox_url}")
                        else:
                            print("Lỗi khi tải lên Catbox.")
                        delete_file(aac_file)
                    else:
                        print("Lỗi khi tải nhạc từ SoundCloud.")

                else:
                    print("Số thứ tự không hợp lệ.")

            except ValueError:
                print("Vui lòng nhập một số thứ tự hợp lệ.")

        else:
            print("Không tìm thấy bài hát nào.")
    else:
        print("Tên bài hát không được bỏ trống.")

if __name__ == "__main__":
    ten_bai_hat_tim_kiem = input("Nhập tên bài hát bạn muốn tìm kiếm: ")
    handle_scl_command(ten_bai_hat_tim_kiem)
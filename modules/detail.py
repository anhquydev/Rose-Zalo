import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import requests
import base64
import emoji
import concurrent.futures
import time
import psutil
import platform
import json
import sys
from zlapi.models import Message

des = {'version': "1.2.4", 'credits': "Vũ Xuân Kiên", 'description': ".", 'power': "Thành viên"}
start_time = time.time()
start_ram_used = psutil.virtual_memory().used
FONT_PATH = "modules/cache/font/BeVietnamPro-Bold.ttf"
EMOJI_FONT_PATH = "modules/cache/font/NotoEmoji-Bold.ttf"
AUTO_APPROVE_PATH = "data/auto_approve_settings.json"
	
def get_font(size):
    return ImageFont.truetype(FONT_PATH, size)

def get_emoji_font(size):
    return ImageFont.truetype(EMOJI_FONT_PATH, size)

def calculate_text_width(text, font, emoji_font):
    return sum(emoji_font.getlength(c) if emoji.emoji_count(c) else font.getlength(c) for c in text)

def split_text_into_lines(text, font, emoji_font, max_width):
    lines, current_line = [], []
    for word in text.split():
        temp_line = " ".join(current_line + [word])
        if calculate_text_width(temp_line, font, emoji_font) <= max_width:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    return lines + [" ".join(current_line)]

def draw_text(draw, text, position, font, emoji_font, image_width, text_color=(255, 255, 255), author_font=None):
    x, y = position
    line_height = int((font.getbbox("Ay")[3] - font.getbbox("Ay")[1]) * 1.5)
    max_width = image_width * 0.9
    all_lines = []
    for line in text.splitlines():
        all_lines.extend(split_text_into_lines(line, font, emoji_font, max_width))
    start_y = y - len(all_lines) * line_height // 2
    for i, line in enumerate(all_lines):
        current_x = x - calculate_text_width(line, author_font if i==0 and author_font else font, emoji_font) // 2
        for char in line:
            f = emoji_font if emoji.emoji_count(char) else (author_font if i==0 and author_font else font)
            draw.text((current_x, start_y), char, fill=text_color, font=f)
            current_x += f.getlength(char)
        start_y += line_height

def make_circle_mask(size):
    mask = Image.new('L', size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size[0], size[1]), fill=255)
    return mask

def draw_circular_avatar(image, avatar_image, position, size):
    if avatar_image:
        image.paste(avatar_image.resize(size), position, mask=make_circle_mask(size))

def calculate_text_height(content, font, emoji_font, image_width):
    dummy_image = Image.new("RGB", (image_width, 1))
    line_height = int((ImageDraw.Draw(dummy_image).textbbox((0, 0), "A", font=font)[3] - ImageDraw.Draw(dummy_image).textbbox((0, 0), "A", font=font)[1]) * 1.4)
    max_width = image_width * 0.9
    all_lines = []
    for line in content.splitlines():
        all_lines.extend(split_text_into_lines(line, font, emoji_font, max_width))
    return len(all_lines) * line_height

def fetch_image(url):
    if not url:
        return None
    try:
        if url.startswith('data:image'):
            return Image.open(BytesIO(base64.b64decode(url.split(',', 1)[1]))).convert("RGB")
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGB")
    except:
        return None

def format_time(seconds):
    days, seconds = divmod(seconds, 24 * 3600)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days} Ngày, {hours} Giờ, {minutes} Phút, {seconds} Giây"

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 ** 2)

def system_info(author_name):
    ram = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage('/')
    ram_usage = (psutil.virtual_memory().used - start_ram_used) / (1024 ** 2)
    uptime = format_time(int(time.time() - start_time))
    cpu_freq = psutil.cpu_freq()
    return f"""
🧭 Thời gian hoạt động:
{uptime}
📜 Hệ điều hành: {platform.system()}
📜 RAM: {ram.used / (1024 ** 2):.2f}/{ram.total / (1024 ** 2):.2f} MB, trống {ram.available / (1024 ** 2):.2f} MB
📜 Swap: {swap.used / (1024 ** 2):.2f}/{swap.total / (1024 ** 2):.2f} MB ({swap.percent}%)
📜 Disk: {disk.used / (1024 ** 3):.2f}/{disk.total / (1024 ** 3):.2f} GB
📜 Tần số CPU: {cpu_freq.current:.2f} Mhz (Max: {cpu_freq.max:.2f} Mhz)
📜 RAM bot sử dụng: {ram_usage:.2f} MB
"""

def process_info_image(avatar_url, author_name, undo_enabled, loctk_enabled, antispam_enabled, event_enabled, antilink_enabled, client, thread_id, interaction_enabled, autosend_enabled, auto_approve_enabled, system_info_text):
    base_font_size = 70
    normal_font = get_font(base_font_size)
    emoji_font = get_emoji_font(base_font_size)
    author_font = get_font(base_font_size + 30)

    combined_text = f"{author_name}\n{system_info_text}\n📊 Cấu hình trong nhóm:\n"
    combined_text += f"🚫 Chống thu hồi tin nhắn: {'Bật ⭕' if undo_enabled else 'Tắt ❌'}\n"
    combined_text += f"🚫 Xóa tin nhắn thô tục: {'Bật ⭕' if loctk_enabled else 'Tắt ❌'}\n"
    combined_text += f"🔰 Chống spam: {'Bật ⭕' if antispam_enabled else 'Tắt ❌'}\n"
    combined_text += f"🔔 Thông báo sự kiện nhóm: {'Bật ⭕' if event_enabled else 'Tắt ❌'}\n"
    combined_text += f"📎 Chặn liên kết: {'Bật ⭕' if antilink_enabled else 'Tắt ❌'}\n"
    combined_text += f"💬 Tương tác với thành viên: {'Bật ⭕' if interaction_enabled else 'Tắt ❌'}\n"
    combined_text += f"📜 Gửi nội dung tự động: {'Bật ⭕' if autosend_enabled else 'Tắt ❌'}\n"
    combined_text += f"👥 Phê duyệt thành viên mới: {'Bật ⭕' if auto_approve_enabled else 'Tắt ❌'}\n"

    text_height = calculate_text_height(combined_text, normal_font, emoji_font, 1600)
    image_width = 2000
    image_height = max(2100, text_height + 200)
    image = Image.new("RGB", (image_width, image_height), color=(50, 50, 50))
    avatar_image = fetch_image(avatar_url)
    if avatar_image:
        image.paste(avatar_image.resize((image_width, image_height)), (0, 0))
        overlay = Image.new("RGBA", (image_width, image_height), (0, 0, 75, 96))
        image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        image = ImageEnhance.Brightness(image).enhance(0.5)
    draw = ImageDraw.Draw(image)
    draw_text(draw, combined_text, (image_width // 2, image_height // 2), normal_font, emoji_font, image_width, text_color=(255, 255, 255), author_font=author_font)
    return image

def admin():
    with open('seting.json','r') as f: return json.load(f).get('account_bot')

def handle_detail_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        settings_paths = {
            "undo": "data/undo_settings.json",
            "loctk": "data/loctk_settings.json",
            "antispam": "data/spam_settings.json",
            "event": "data/event_setting.json",
            "antilink": "data/antilink_settings.json",
            "interaction": "modules/cache/duyetboxdata.json",
            "autosend": "modules/cache/sendtask_autosend.json"
        }
        settings = {}
        for key, path in settings_paths.items():
            if os.path.exists(path):
                with open(path, "r") as f:
                    settings[key] = json.load(f)

        undo_enabled = settings.get("undo", {}).get("groups", {}).get(str(thread_id), False)
        loctk_enabled = settings.get("loctk", {}).get(str(thread_id), False)
        antispam_enabled = settings.get("antispam", {}).get(str(thread_id), False)
        event_enabled = str(thread_id) in settings.get("event", {}).get("groups", [])
        antilink_enabled = settings.get("antilink", {}).get(str(thread_id), False)
        interaction_enabled = bool(settings.get("interaction", []) and str(thread_id) in settings["interaction"])
        autosend_enabled = str(thread_id) in settings.get("autosend",{}).get("groups",[])
        auto_approve_settings = {}
        if os.path.exists(AUTO_APPROVE_PATH):
            with open(AUTO_APPROVE_PATH, "r") as f:
                auto_approve_settings = json.load(f)
        auto_approve_enabled = auto_approve_settings.get(str(thread_id), False)
        user_id_to_fetch = admin()
        user_info = client.fetchUserInfo(user_id_to_fetch) or {}
        user_data = user_info.get('changed_profiles', {}).get(user_id_to_fetch, {})
        avatar_url = user_data.get("avatar", None)
        author_name = user_data.get("displayName", "Unknown")
        system_info_text = system_info(author_name)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            image = executor.submit(
                process_info_image,
                avatar_url,
                author_name,
                undo_enabled,
                loctk_enabled,
                antispam_enabled,
                event_enabled,
                antilink_enabled,
                client,
                thread_id,
                interaction_enabled,
                autosend_enabled,
                auto_approve_enabled,
                system_info_text
            ).result()

        output_path = "modules/cache/VXKZALOBOT.jpg"
        image.save(output_path, quality=100)
        if os.path.exists(output_path):
            client.sendLocalImage(output_path, thread_id=thread_id, thread_type=thread_type, width=image.width, height=image.height)
            os.remove(output_path)
    except Exception as e:
        client.sendMessage(Message(text=f"• Đã xảy ra lỗi: {str(e)}"), thread_id, thread_type)

def ft_vxkiue():
    return {'detail': handle_detail_command}
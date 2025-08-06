import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import requests
import base64
import emoji
from datetime import datetime
import concurrent.futures
import textwrap
from zlapi.models import Message, Mention

des = {'version': "1.2.4", 'credits': "Vũ Xuân Kiên", 'description': ".", 'power': "Thành viên"}

def draw_text_line(draw, text, x, y, font, emoji_font, text_color):
    for char in text:
        f = emoji_font if emoji.emoji_count(char) > 0 else font
        draw.text((x, y), char, fill=text_color, font=f)
        x += f.getlength(char)

def split_text_into_lines(text, font, emoji_font, max_width):
    lines = []
    for paragraph in text.splitlines():
        words = paragraph.split()
        line = ""
        for word in words:
            temp_line = line + word + " "
            width = sum(emoji_font.getlength(c) if emoji.emoji_count(c) else font.getlength(c) for c in temp_line)
            if width <= max_width:
                line = temp_line
            else:
                if line:
                    lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())
    return lines

def draw_text(draw, text, position, font, emoji_font, image_width, is_long_text):
    x, y = position
    padding = int(image_width * 0.02)
    max_width = int(image_width) - 2 * padding
    lines = split_text_into_lines(text, font, emoji_font, max_width)
    th = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
    lh = int(th * 1.4)
    yh = len(lines) * lh
    yo = y - yh // 2

    if is_long_text:
        yo += lh // 8
    else:
        yo -= lh // 8
    
    yo = max(padding + lh // 2, yo)
    yo = min(position[1] + yh // 2 - lh //2 -padding, yo)

    for line in lines:
        w = sum(emoji_font.getlength(c) if emoji.emoji_count(c) else font.getlength(c) for c in line)
        draw_text_line(draw, line, x - w // 2, yo, font, emoji_font, (255, 255, 255))
        yo += lh

def get_font_size(size=60):
    return ImageFont.truetype("modules/cache/font/BeVietnamPro-SemiBold.ttf", size)

def make_circle_mask(size):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    return mask

def draw_circular_avatar(image, avatar_image, position, size):
    mask = make_circle_mask(size)
    image.paste(avatar_image.resize(size), position, mask=mask)

def calculate_text_height(content, font, image_width):
    lines = split_text_into_lines(content, font, ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", font.size), int(image_width * 0.96))
    th = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
    lh = int(th * 1.2)
    return len(lines) * lh

def fetch_image(url):
    if not url: return None
    try:
        if url.startswith('data:image'):
            h, e = url.split(',', 1)
            try:
                i = base64.b64decode(e)
            except:
                return None
            return Image.open(BytesIO(i)).convert("RGB")
        r = requests.get(url, stream=True, timeout=10)
        r.raise_for_status()
        return Image.open(BytesIO(r.content)).convert("RGB")
    except:
        return None
    
def process_image(avatar_url, cover_url, content, author_name):
    dw, dh = 1500, 1000
    f = get_font_size()
    text_height = calculate_text_height(content, f, dw)
    iw, ih = dw, max(dh + text_height + 1, dh + 1)
    hh = 280
    hi = Image.new("RGB", (iw, hh), color=(255, 255, 255))
    mi = Image.new("RGB", (iw, ih - hh), color=(50, 50, 50))
    ci = fetch_image(cover_url)
    if ci:
        mi.paste(ci.resize((iw, ih - hh)), (0, 0))
        mi = ImageEnhance.Brightness(mi).enhance(0.3)
    image = Image.new("RGB", (iw, ih), color=(50, 50, 50))
    image.paste(hi, (0, 0))
    image.paste(mi, (0, hh))
    ai = fetch_image(avatar_url)
    if ai:
        ax, ay, sz = 50, 34, (222, 222)
        draw_circular_avatar(image, ai, (ax, ay), sz)
        draw = ImageDraw.Draw(image)
        sx1, sy1, sx2, sy2 = ax + sz[0] + 20, 50, ax + sz[0] + 20, 240
        draw.line((sx1, sy1, sx2, sy2), fill=(150, 150, 150), width=3)
        nf = get_font_size(66)
        en = ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", nf.size)
        draw_text_line(draw, author_name, sx1 + 20, 93, nf, en, (0, 0, 0))
        ft = datetime.now().strftime("%H:%M %d-%m-%Y 🌎")
        tf = get_font_size(30)
        et = ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", tf.size)
        draw_text_line(draw, ft, sx1 + 20, 165, tf, et, (150, 150, 150))
    draw = ImageDraw.Draw(image)
    f = get_font_size()
    ef = ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", f.size)
    ty = (ih + hh) // 2

    is_long_text = len(content) > 50  
    draw_text(draw, content, (iw // 2, ty), f, ef, iw, is_long_text)
    return image

def handle_canvas_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        parts = message.split(" ", 1)
        if len(parts) < 2:
            client.replyMessage(Message(text="@Member, vui lòng nhập nội dung cần tạo ảnh.", mention=Mention(author_id, length=len("@Member"), offset=0)), message_object, thread_id, thread_type)
            return
        c = parts[1]

        uid = client.fetchPhoneNumber(author_id, language="vi") or {}
        if not uid or not uid.get('uid'):
            u = client.fetchUserInfo(author_id) or {}
        else:
             u = client.fetchUserInfo(uid.get('uid', author_id)) or {}

        ud = u.get('changed_profiles', {}).get(uid.get('uid', author_id), {}) if uid.get('uid') else u.get('changed_profiles', {}).get(author_id, {})
        av, cv = ud.get('avatar'), ud.get('cover')
        ai = client.fetchUserInfo(author_id).get('changed_profiles', {}).get(author_id, {})
        an = ai.get('zaloName', 'đéo xác định')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            image = executor.submit(process_image, av, cv, c, an).result()
        op = "modules/cache/VXKZALOBOT.jpg"
        image.save(op, quality=70)
        try:
            if os.path.exists(op):
                client.sendLocalImage(op, thread_id=thread_id, thread_type=thread_type, width=image.width, height=image.height)
        finally:
            if os.path.exists(op):
                os.remove(op)
    except Exception as e:
        client.sendMessage(Message(text=f"• Đã xảy ra lỗi: {str(e)}"), thread_id, thread_type)

def ft_vxkiue():
    return {'canvas': handle_canvas_command}
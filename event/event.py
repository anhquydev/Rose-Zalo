import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import requests
import base64
import emoji
from datetime import datetime
import concurrent.futures
import json
from zlapi.models import *

des = {'version': "1.3.0", 'credits': "Anh Quý", 'description': "weo căm", 'power': "Thành viên"}

EVENT_SETTINGS_FILE = "data/event_setting.json"
DEFAULT_COVER_PATH = "modules/cache/vxkiue.jpg"

def load_allowed_groups():
    if os.path.exists(EVENT_SETTINGS_FILE):
        with open(EVENT_SETTINGS_FILE, "r") as f:
            return json.load(f).get("groups", [])
    return []

def draw_text_line(draw, text, x, y, font, emoji_font, text_color):
    for char in text:
        f = emoji_font if emoji.emoji_count(char) else font
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

def draw_text(draw, text, position, font, emoji_font, image_width, separator_x, is_long_text):
    x, y = position
    max_width = image_width - separator_x
    lines = split_text_into_lines(text, font, emoji_font, max_width)
    th = font.getbbox("Ay")[3] - font.getbbox("Ay")[1]
    lh = int(th * 1.4)
    yh = len(lines) * lh
    yo = y - yh // 2

    if is_long_text and len(lines) > 5:
        lines = lines[:5]
        lines[-1] = lines[-1][:max(0, len(lines[-1]) - 3)] + "..."
        yh = len(lines) * lh
        yo = y - yh // 2

    yo += lh // 8
    start_x = separator_x + (max_width - sum(emoji_font.getlength(c) if emoji.emoji_count(c) else font.getlength(c) for c in lines[0])) // 2 if lines else separator_x

    for line in lines:
        line_width = sum(emoji_font.getlength(c) if emoji.emoji_count(c) else font.getlength(c) for c in line)
        start_x = separator_x + (max_width - line_width) // 2
        draw_text_line(draw, line, start_x, yo, font, emoji_font, (255, 255, 255))
        yo += lh

def get_font_size(size=60):
    return ImageFont.truetype("modules/cache/font/BeVietnamPro-Bold.ttf", size)

def make_circle_mask(size, border_width=0):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((border_width, border_width, size[0]-border_width, size[1]-border_width), fill=255)
    return mask

def draw_stylized_avatar(image, avatar_image, position, size, border_color=(220, 220, 220), border_thickness=15):
    scale = 7
    scaled_size = (size[0] * scale, size[1] * scale)
    scaled_border_thickness = border_thickness * scale
    inner_scaled_size = (scaled_size[0] - 2 * scaled_border_thickness, scaled_size[1] - 2 * scaled_border_thickness)
    avatar_scaled = avatar_image.resize(inner_scaled_size, resample=Image.LANCZOS)
    mask_scaled = make_circle_mask(inner_scaled_size)
    border_img = Image.new("RGBA", scaled_size, (0, 0, 0, 0))
    draw_obj = ImageDraw.Draw(border_img)
    draw_obj.ellipse((0, 0, scaled_size[0] - 1, scaled_size[1] - 1), fill=border_color + (255,))
    border_img.paste(avatar_scaled, (scaled_border_thickness, scaled_border_thickness), mask=mask_scaled)
    border_img = border_img.resize(size, resample=Image.LANCZOS)
    image.paste(border_img, position, mask=border_img)

def calculate_text_height(content, font, image_width):
    lines = split_text_into_lines(content, font, ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", font.size), int(image_width * 0.6))
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

def process_image(avatar_url, cover_url, content, author_name, event_time):
    dw, dh = 2000, 760
    f = get_font_size()
    text_height = calculate_text_height(content, f, dw)
    cover_width, cover_height = 2000, 760
    avatar_size = 325
    avatar_x = int(dw * 0.03)
    avatar_y = int(dh * 0.5 - avatar_size * 0.5)

    if cover_url == "https://cover-talk.zadn.vn/default" and os.path.exists(DEFAULT_COVER_PATH):
        try:
            ci = Image.open(DEFAULT_COVER_PATH).convert("RGB")
        except:
            ci = None
    else:
        ci = fetch_image(cover_url)

    if ci:
        ci = ci.resize((cover_width, cover_height))

    text_region_height = text_height + 20
    min_height = max(avatar_y + avatar_size + 50,  280 + text_region_height)
    iw, ih = dw, max(min_height, dh)
    image = Image.new("RGB", (iw, ih), color=(50, 50, 50))

    if ci:
        mi = ci.copy()
        mi = ImageEnhance.Brightness(mi).enhance(0.6)
        image.paste(mi.resize((iw, ih)), (0, 0))

    ai = fetch_image(avatar_url)
    if ai:
        draw_stylized_avatar(image, ai, (avatar_x, avatar_y), (avatar_size, avatar_size), border_color=(220, 220, 220))

        draw = ImageDraw.Draw(image)
        separator_x = avatar_x * 2 + avatar_size
        draw.line((separator_x, avatar_y, separator_x, avatar_y + avatar_size), fill=(150, 150, 150), width=8)

    draw = ImageDraw.Draw(image)
    f = get_font_size(70)
    ef = ImageFont.truetype("modules/cache/font/NotoEmoji-Bold.ttf", f.size)

    text_x = separator_x
    text_y = ih // 2
    is_long_text = len(content) > 20
    draw_text(draw, content, (text_x, text_y), f, ef, iw, separator_x, is_long_text)

    return image

def buildWelcomeMessage(self, groupName, joinMembers, sourceId=None, is_join_request=False, group_type_name="Cộng Đồng"):
    member_list = ', '.join([member.get('dName') for member in joinMembers])
    if sourceId:
        adder_info = self.fetchUserInfo(sourceId)
        adder_name = adder_info["changed_profiles"][sourceId].get("displayName", "Không xác định") if adder_info and "changed_profiles" in adder_info and sourceId in adder_info["changed_profiles"] else "Không xác định"
        if adder_name != "Không xác định":
            if is_join_request:
                text = f"{groupName}\nChào Mừng {member_list}\nĐã Tham Gia {group_type_name}\nDuyệt Bởi {adder_name}"
            else:
                text = f"{groupName}\nChào Mừng {member_list}\nĐã Tham Gia {group_type_name}\nTham Gia Trực Tiếp Từ Link Hoặc Được Mời"

    return text

def buildLeaveMessage(self, groupName, updateMembers, eventType, sourceId=None, group_type_name="Cộng Đồng"):
    member_name = updateMembers[0].get('dName')

    if eventType == GroupEventType.LEAVE:
        text = f"Member Left The Group\n{member_name}\nVừa Rời Khỏi {group_type_name}\n{groupName}"
    elif eventType == GroupEventType.REMOVE_MEMBER:
        remover_info = self.fetchUserInfo(sourceId)
        remover_name = remover_info["changed_profiles"][sourceId].get("displayName", "Không xác định") if remover_info and "changed_profiles" in remover_info and sourceId in remover_info["changed_profiles"] else "Không xác định"
        if remover_name != "Không xác định":
            text = f"Kick Out Member\n{member_name}\nĐã Bị {remover_name} Sút Khỏi {group_type_name}\n{groupName}"
        else:
            text = f"Kick Out Member\n{member_name}\nĐã Bị Sút Khỏi {group_type_name} {groupName}."
    else:
        return

    return text

def handleGroupEvent(self, eventData, eventType):
    groupId = eventData.get('groupId')
    if not groupId:
        return

    allowed_groups = load_allowed_groups()
    if groupId not in allowed_groups:
        return

    group_type = self.fetchGroupInfo(groupId).gridInfoMap[groupId].type
    group_type_name = "Cộng Đồng" if group_type == 2 else "Nhóm"

    if eventType == GroupEventType.JOIN:
        groupName = eventData.get('groupName', "group")
        joinMembers = eventData.get('updateMembers', [])
        sourceId = eventData.get("sourceId")
        is_join_request = False
        if sourceId and not any(sourceId == member.get("id") for member in joinMembers):
            is_join_request = True

        if not joinMembers:
            return

        text = buildWelcomeMessage(self, groupName, joinMembers, sourceId, is_join_request, group_type_name)
        event_time = datetime.now()
        memberIds = [member.get('id') for member in joinMembers]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for member_id in memberIds:
                executor.submit(process_group_event_image, self, member_id, text, groupId, event_time, "VXKZALOBOT_welcome.jpg", has_mention=True)

    elif eventType in {GroupEventType.LEAVE, GroupEventType.REMOVE_MEMBER}:
        groupName = eventData.get('groupName', "group")
        updateMembers = eventData.get('updateMembers', [])
        sourceId = eventData.get("sourceId")

        if not updateMembers:
            return

        text = buildLeaveMessage(self, groupName, updateMembers, eventType, sourceId, group_type_name)
        event_time = datetime.now()
        memberIds = [member.get('id') for member in updateMembers]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for member_id in memberIds:
                executor.submit(process_group_event_image, self, member_id, text, groupId, event_time, "VXKZALOBOT_leave.jpg", has_mention=False)

    elif eventType == GroupEventType.REMOVE_ADMIN:
        groupName = eventData.get('groupName', "group")
        updateMembers = eventData.get('updateMembers', [])
        ow_id = eventData.get("sourceId")

        if not updateMembers:
            return

        member_name = updateMembers[0].get('dName')
        ow_name = self.fetchUserInfo(ow_id).get('changed_profiles', {}).get(ow_id, {}).get('displayName', "Không xác định") if self.fetchUserInfo(ow_id) and self.fetchUserInfo(ow_id).get('changed_profiles') and ow_id in self.fetchUserInfo(ow_id).get('changed_profiles') else "Không xác định"
        text = f'{groupName}\n{member_name}\nĐã Được {ow_name} Cho Bay Màu Khỏi Kanh Sách Quản Trị Viên {group_type_name}'
        event_time = datetime.now()
        member_id = updateMembers[0].get('id')
        process_group_event_image(self, member_id, text, groupId, event_time, "VXKZALOBOT_remove_admin.jpg", has_mention=True)

    elif eventType == GroupEventType.ADD_ADMIN:
        groupName = eventData.get('groupName', "group")
        updateMembers = eventData.get('updateMembers', [])
        ow_id = eventData.get("sourceId")

        if not updateMembers:
            return

        member_name = updateMembers[0].get('dName')
        ow_name = self.fetchUserInfo(ow_id).get('changed_profiles', {}).get(ow_id, {}).get('displayName', "Không xác định") if self.fetchUserInfo(ow_id) and self.fetchUserInfo(ow_id).get('changed_profiles') and ow_id in self.fetchUserInfo(ow_id).get('changed_profiles') else "Không xác định"
        text = f'{groupName}\n{member_name}\nĐã Được {ow_name} Bổ Nhiệm Làm Quản Trị Viên {group_type_name}'
        event_time = datetime.now()
        member_id = updateMembers[0].get('id')
        process_group_event_image(self, member_id, text, groupId, event_time, "VXKZALOBOT_add_admin.jpg", has_mention=True)

def process_group_event_image(self, member_id, text, groupId, event_time, filename, has_mention=False):
    u = self.fetchUserInfo(member_id) or {}
    ud = u.get('changed_profiles', {}).get(member_id, {})
    av, cv = ud.get('avatar'), ud.get('cover')
    ai = self.fetchUserInfo(member_id).get('changed_profiles', {}).get(member_id, {})
    an = ai.get('zaloName', 'đéo xác định')
    image = process_image(av, cv, text, an, event_time)
    op = os.path.join("modules/cache", filename)
    image.save(op, quality=100)
    try:
        if has_mention:
            self.sendLocalImage(op, thread_id=groupId, thread_type=ThreadType.GROUP, width=image.width, height=image.height, message=Message(text="@Member", mention=Mention(member_id, length=len("@Member"), offset=0)),)
        else:
            self.sendLocalImage(op, thread_id=groupId, thread_type=ThreadType.GROUP, width=image.width, height=image.height)

    except Exception as e:
        print(f"Error sending image: {e}")
    finally:
        if os.path.exists(op):
            os.remove(op)

def ft_vxkiue():
    return {}
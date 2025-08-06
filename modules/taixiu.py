import json
import random
import os
from PIL import Image
from zlapi.models import *

des = {
    'version': "1.0.9",
    'credits': "Vũ Xuân Kiên",
    'description': "Chơi game Tài Xỉu",
    'power': "Thành viên"
}

def load_money_data():
    try:
        with open('modules/cache/money.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_money_data(data):
    with open('modules/cache/money.json', 'w') as f:
        json.dump(data, f, indent=4)

def format_money(amount):
    return f"{amount:,} VNĐ"

def get_user_name(client, user_id):
    try:
        user_info = client.fetchUserInfo(user_id)
        profile = user_info.changed_profiles.get(user_id, {})
        user_name = profile.get('zaloName', 'Không xác định')
    except AttributeError:
        user_name = 'Không xác định'
    return user_name

def merge_images(image_paths, output_path):
    images = [Image.open(img) for img in image_paths]
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    new_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0

    for img in images:
        new_image.paste(img, (x_offset, 0))
        x_offset += img.width

    new_image.save(output_path)

def parse_bet_amount(text, current_balance):
    text = text.lower()
    if text == "all":
        return current_balance, None
    if text.endswith('%'):
        try:
            percent = float(text[:-1])
            if 1 <= percent <= 100:
                return int(current_balance * (percent / 100)), None
            else:
                return 0, "• Phần trăm phải từ 1% đến 100%."
        except ValueError:
            return 0, "• Phần trăm không hợp lệ."
    
    multiplier = 1
    if text.endswith('k'):
        multiplier = 1000
        text = text[:-1]
    elif text.endswith('m'):
        multiplier = 1000000
        text = text[:-1]
    elif text.endswith('b'):
       multiplier = 1000000000
       text = text[:-1]

    try:
        amount = int(float(text) * multiplier)
        return amount, None
    except ValueError:
        return 0, "• Số tiền không hợp lệ."


def handle_taixiu_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()
    money_data = load_money_data()
    response_message = ""
    data_trave = ""
    dice_values = []

    if len(text) < 3 or text[1] not in ["tài", "xỉu"]:
        response_message = "• Lệnh không hợp lệ. Sử dụng: taixiu <tài hoặc xỉu> <số tiền hoặc all hoặc % số tiền>"
    else:
        choice = text[1]
        current_balance = money_data.get(str(author_id), 0)

        if len(text) == 3:
            bet_amount, error = parse_bet_amount(text[2], current_balance)
            if error:
                response_message = error
            else:
                if bet_amount > current_balance:
                    response_message = "• Số dư của bạn không đủ để đặt cược."
                elif bet_amount <= 0:
                    response_message = "• Số tiền cược phải lớn hơn 0."
                else:
                    dice_values = [random.randint(1, 6) for _ in range(3)]
                    total_points = sum(dice_values)
                    result = "xỉu" if total_points % 2 == 0 else "tài"
                    outcome = "thắng" if choice == result else "thua"
                    
                    if outcome == "thắng":
                        multiplier = 2
                        if dice_values.count(dice_values[0]) == 2 or dice_values.count(dice_values[1]) == 2:
                            multiplier = 2
                        elif dice_values.count(dice_values[0]) == 3:
                            multiplier = 10
                        money_data[str(author_id)] = current_balance + (bet_amount * multiplier)
                        response = f"Đã cộng {format_money(bet_amount * multiplier)} vào số dư.\n"
                    else:
                        money_data[str(author_id)] = current_balance - bet_amount
                        response = f"Đã trừ {format_money(bet_amount)} khỏi số dư.\n"

                    save_money_data(money_data)
                    author_name = get_user_name(client, author_id)

                    data_trave = (
                        f"[ {author_name} ]\n\n"
                        f"• Bạn đã đặt cược {format_money(bet_amount)} VNĐ vào {choice.capitalize()}.\n"
                        "• Kết quả trả về là:\n"
                        f"> Xúc xắc 1: {dice_values[0]}\n"
                        f"> Xúc xắc 2: {dice_values[1]}\n"
                        f"> Xúc xắc 3: {dice_values[2]}\n"
                        f"• Tổng điểm: {total_points} ({'Xỉu' if result == 'xỉu' else 'Tài'})\n"
                        f"• Bạn đã {outcome}\n"
                        f"• {response}"
                    )

                    gui = Message(text=data_trave)
        else:
            response_message = "• Lệnh không hợp lệ. Sử dụng: taixiu <tài hoặc xỉu> <số tiền hoặc all hoặc % số tiền>"
            bet_amount = 0
    
    client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)
    
    if dice_values:
        image_paths = [f'modules/taixiu/{value}.jpg' for value in dice_values]
        merged_image_path = "modules/taixiu/merged_dice.jpg"

        if all(os.path.exists(path) for path in image_paths):
            merge_images(image_paths, merged_image_path)

            t = Message(text=f"{author_name}")
            client.sendLocalImage(
                imagePath=merged_image_path,
                message=gui,
                thread_id=thread_id,
                thread_type=thread_type,
                width=921,
                height=308
            )

            os.remove(merged_image_path)
        else:
            response_message += "\n• Không thể hiển thị hình ảnh kết quả do thiếu hình ảnh xúc xắc."
            client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'taixiu': handle_taixiu_command
    }
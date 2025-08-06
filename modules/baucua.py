import json
import random
import os
from PIL import Image
from zlapi.models import *

des = {
    'version': "1.0.9",
    'credits': "Vũ Xuân Kiên",
    'description': "Chơi game Bầu Cua",
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

def handle_baucua_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()
    money_data = load_money_data()
    response_message = ""
    data_trave = ""
    dice_results = []
    baucua_options = ["bầu", "cua", "tôm", "cá", "gà", "nai"]

    if len(text) < 3:
        response_message = "• Lệnh không hợp lệ. Sử dụng: bc <bầu|cua|tôm|cá|gà|nai> <số tiền hoặc all hoặc % số tiền>"
    else:
      choices = text[1:-1]
      if any(item.lower() not in baucua_options for item in choices):
          response_message = "• Lệnh không hợp lệ. Sử dụng: bc <bầu|cua|tôm|cá|gà|nai> <số tiền hoặc all hoặc % số tiền>"
      else:
        if len(choices) > 3:
            response_message = "• Chỉ được đặt tối đa 3 con."
        else:
            current_balance = money_data.get(str(author_id), 0)
            bet_amount_text = text[-1]
            bet_amount, error = parse_bet_amount(bet_amount_text, current_balance)
            if error:
                response_message = error
            else:
                if bet_amount > current_balance:
                    response_message = "• Số dư của bạn không đủ để đặt cược."
                elif bet_amount <= 0:
                    response_message = "• Số tiền cược phải lớn hơn 0."
                else:
                  dice_results = [random.choice(baucua_options) for _ in range(3)]
                  win_amount = 0
                  win_details = []
                  
                  
                  
                  if len(choices) == 1:
                      choice = choices[0]
                      win_count = dice_results.count(choice)
                      if win_count > 0:
                         if win_count == 1:
                            win_amount += bet_amount * 2
                            win_details.append(f"{choice.capitalize()}: x2")
                         elif win_count == 2:
                            win_amount += bet_amount * 3
                            win_details.append(f"{choice.capitalize()}: x3")
                         elif win_count == 3:
                            win_amount += bet_amount * 4
                            win_details.append(f"{choice.capitalize()}: x4")
                      else:
                           win_amount -= bet_amount
                           win_details.append(f"{choice.capitalize()}: mất tiền")


                  elif len(choices) == 2:
                      total_win_amount = 0
                      for choice in choices:
                          win_count = dice_results.count(choice)
                          if win_count > 0 :
                            if win_count == 1:
                                total_win_amount += bet_amount * 2
                                win_details.append(f"{choice.capitalize()}: x2")
                            elif win_count == 2:
                                total_win_amount += bet_amount * 3
                                win_details.append(f"{choice.capitalize()}: x3")
                            elif win_count == 3:
                                total_win_amount += bet_amount * 4
                                win_details.append(f"{choice.capitalize()}: x4")
                      if total_win_amount == 0:
                         for choice in choices:
                            if dice_results.count(choice) == 0:
                                win_details.append(f"{choice.capitalize()}: mất tiền")
                                win_amount -= bet_amount
                            
                      win_amount += total_win_amount *2 if total_win_amount > 0 else win_amount



                  elif len(choices) == 3:
                       total_win_amount = 0
                       for choice in choices:
                           win_count = dice_results.count(choice)
                           if win_count > 0:
                             if win_count == 1:
                                 total_win_amount += bet_amount * 2
                                 win_details.append(f"{choice.capitalize()}: x2")
                             elif win_count == 2:
                                  total_win_amount += bet_amount * 3
                                  win_details.append(f"{choice.capitalize()}: x3")
                             elif win_count == 3:
                                  total_win_amount += bet_amount * 4
                                  win_details.append(f"{choice.capitalize()}: x4")
                       if total_win_amount == 0:
                            for choice in choices:
                                if dice_results.count(choice) == 0:
                                    win_details.append(f"{choice.capitalize()}: mất tiền")
                                    win_amount -= bet_amount
                       win_amount += total_win_amount * 10 if total_win_amount > 0 else win_amount
                  
                  
                

                  
                  if win_amount > 0:
                      money_data[str(author_id)] = current_balance + win_amount
                      response = f"Đã cộng {format_money(win_amount)} vào số dư.\n"
                      outcome = "thắng"
                  else:
                      money_data[str(author_id)] = current_balance + win_amount
                      response = f"Đã trừ {format_money(abs(win_amount))} khỏi số dư.\n" if win_amount <0 else "Bạn đã không trúng con nào.\n"
                      outcome = "thua"

                  save_money_data(money_data)
                  author_name = get_user_name(client, author_id)

                  bet_text = ", ".join([c.capitalize() for c in choices])
                  win_detail_text = ", ".join(win_details) if win_details else "Không trúng con nào."
                  data_trave = (
                      f"[ {author_name} ]\n\n"
                      f"• Bạn đã đặt cược {format_money(bet_amount)} VNĐ vào {bet_text}.\n"
                      "• Kết quả trả về là:\n"
                      f"> Bầu cua 1: {dice_results[0].capitalize()}\n"
                      f"> Bầu cua 2: {dice_results[1].capitalize()}\n"
                      f"> Bầu cua 3: {dice_results[2].capitalize()}\n"
                      f"• Bạn đã {outcome}. {win_detail_text}\n"
                      f"• {response}"
                  )
                  gui = Message(text=data_trave)

    client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)

    if dice_results:
        image_paths = [f'modules/baucua/{result}.jpg' for result in dice_results]
        merged_image_path = "modules/baucua/merged_baucua.jpg"

        if all(os.path.exists(path) for path in image_paths):
            merge_images(image_paths, merged_image_path)

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
            response_message += "\n• Không thể hiển thị hình ảnh kết quả do thiếu hình ảnh bầu cua."
            client.replyMessage(Message(text=response_message), message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'baucua': handle_baucua_command
    }
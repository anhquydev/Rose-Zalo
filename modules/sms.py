import os
import datetime
import subprocess
from zlapi.models import MultiMsgStyle, Mention, MessageStyle, Message
import time

des = {
    'version': "1.9.2",
    'credits': "Quốc Khánh",
    'description': "spam sms",
    'power': "Thành viên"
}

def handle_sms_command(message, message_object, thread_id, thread_type, author_id, client):
    parts = message.split()

    if len(parts) == 1:
        client.replyMessage(
            Message(text='Vui lòng nhập số điện thoại sau lệnh.'),
            message_object,
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    attack_phone_number = parts[1]
    
    if not attack_phone_number.isnumeric() or len(attack_phone_number) != 10:
        client.replyMessage(
            Message(text='Số điện thoại không hợp lệ! Vui lòng nhập đúng số.'),
            message_object,
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    if attack_phone_number in ['113', '911', '114', '115', '0345864723']:
        client.replyMessage(
            Message(text="Số này không thể spam!"),
            message_object,
            thread_id=thread_id,
            thread_type=thread_type
        )
        return

    current_time = datetime.datetime.now()
    if author_id in client.last_sms_times:
        last_sent_time = client.last_sms_times[author_id]
        elapsed_time = (current_time - last_sent_time).total_seconds()
        if elapsed_time < 120:
            client.replyMessage(
                Message(text="Vui lòng chờ 120 giây và thử lại!"),
                message_object,
                thread_id=thread_id,
                thread_type=thread_type
            )
            return

    client.last_sms_times[author_id] = current_time

    file_path1 = os.path.join(os.getcwd(), "data/smsv2.py")
    subprocess.Popen(["python", file_path1, attack_phone_number, "7"])

    now = datetime.datetime.now()
    time_str = now.strftime("%d/%m/%Y %H:%M:%S")
    masked_phone_number = f"{attack_phone_number[:3]}***{attack_phone_number[-3:]}"
    msg_content = f'''@Member

    Bot Spam Call Và SMS
 
 PHONE :
   ├─> {masked_phone_number} 
   ├─────────────⭔
 TIME :
   ├─> {time_str} 
   ├─────────────⭔
 COOLDOWN :
   ├─> 120 giây
   ├─────────────⭔
 ZALO ADMIN :
   ├─> 0345864723
   └─────────────⭔
    '''

    image_path = os.path.join(os.getcwd(), "modules", "cache", "sms.jpg")

    mention = Mention(author_id, length=len("@Member"), offset=0)
    client.sendLocalImage(
        image_path,
        thread_id=thread_id,
        thread_type=thread_type,
        width=720,
        height=450,
        message=Message(text=msg_content, mention=mention)
    )

def ft_vxkiue():
    return {
        'sms': handle_sms_command
    }

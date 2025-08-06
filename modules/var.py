from zlapi.models import Message, Mention, MultiMsgStyle, MessageStyle
import time
import threading
from config import ADMIN
import logging

des = {
    'version': "1.0.3",
    'credits': "Nguyễn Đức Tài",
    'description': "Kết hợp chức năng tagall và chửi",
    'power': "Quản trị viên Bot"
}

is_var_running = False

def stop_var(client, message_object, thread_id, thread_type):
    global is_var_running
    is_var_running = False
    client.replyMessage(Message(text="Success!"), message_object, thread_id, thread_type)

def check_admin_permissions(author_id, creator_id, admin_ids):
    all_admin_ids = set(admin_ids)
    all_admin_ids.add(creator_id)
    all_admin_ids.update(ADMIN)
    return author_id in all_admin_ids
    
def send_error_message(client, thread_id, thread_type, error_message):
        client.replyMessage(Message(text=error_message), None, thread_id, thread_type)

def handle_var_command(message, message_object, thread_id, thread_type, author_id, client):
    global is_var_running
    command_parts = message.split()
    if len(command_parts) < 2:
        client.replyMessage(Message(text="on/off"), message_object, thread_id, thread_type)
        return
        
    group_info = client.fetchGroupInfo(thread_id)
    if not group_info or thread_id not in group_info.gridInfoMap:
        send_error_message(client, thread_id, thread_type, "Không thể lấy thông tin nhóm.")
        return
    group_data = group_info.gridInfoMap[thread_id]
    creator_id = group_data.get('creatorId')
    admin_ids = group_data.get('adminIds', [])
    if not check_admin_permissions(author_id, creator_id, admin_ids):
        send_error_message(client, thread_id, thread_type, "Chỉ key bạc, key vàng, admin mới có thể sử dụng.")
        return
    
    action = command_parts[1].lower()

    if action == "off":
        if not is_var_running:
            client.replyMessage(Message(text="Success!"), message_object, thread_id, thread_type)
        else:
            stop_var(client, message_object, thread_id, thread_type)
        return

    if action != "on":
        client.replyMessage(Message(text="on/off"), message_object, thread_id, thread_type)
        return
    
    try:
        with open("data/noidung.txt", "r", encoding="utf-8") as file:
            Ngon = file.readlines()
    except FileNotFoundError:
        send_error_message(client, thread_id, thread_type, "Không tìm thấy tệp noidung.txt")
        return
    except Exception as e:
        send_error_message(client, thread_id, thread_type, f"Lỗi khi đọc tệp: {e}")
        return
    if not Ngon:
        send_error_message(client, thread_id, thread_type, "Tệp nội dung rỗng")
        return
    
    is_var_running = True
    def var_loop():
        while is_var_running:
             for noidung in Ngon:
                if not is_var_running:
                   break
                noidung = noidung.strip()
                mention = Mention("-1", length=len(noidung), offset=0)
                styles = MultiMsgStyle([
                MessageStyle(offset=0, length=10000, style="font", size="100000", auto_format=False),
                MessageStyle(offset=0, length=10000, style="bold", size="100000", auto_format=False),                
                MessageStyle(offset=0, length=10000, style="color", color="#db342e", auto_format=False),
            ])
                client.send(Message(text=noidung, mention=mention, style=styles), thread_id, thread_type)
                time.sleep(0.5)
    
    var_thread = threading.Thread(target=var_loop)
    var_thread.start()
    
def ft_vxkiue():
    return {
        'var': handle_var_command
    }
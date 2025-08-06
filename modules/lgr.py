import json
from zlapi.models import *
from config import ADMIN
import os
import time
from zlapi.models import MultiMsgStyle, MessageStyle

des = {
    'version': '1.0.6',
    'credits': 'Vũ Xuân Kiên',
    'description': 'list group',
    'power': "Quản trị viên Bot"
}

def is_admin(author_id):
    return author_id == ADMIN

def load_duyetbox_data():
    file_path = 'modules/cache/duyetboxdata.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

def handle_lgr_command(message, message_object, thread_id, thread_type, author_id, client):
    styles = MultiMsgStyle([
                MessageStyle(offset=0, length=10000, style="font", size="10", auto_format=False),
            ])
    if not is_admin(author_id):
        response_message = "Bạn không có quyền sử dụng lệnh này."
        client.replyMessage(Message(text=response_message, style=styles), message_object, thread_id, thread_type)
        return

    data = load_duyetbox_data()
    excluded_group_id = "4009464343109121790"
    all_groups = client.fetchAllGroups().gridVerMap.keys()
    group_list = []

    for group_id in all_groups:
        if group_id == excluded_group_id:
            continue
        group_info = client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {})
        group_name = group_info.get('name', 'None')
        status = "Đã duyệt" if group_id in data else "Chưa duyệt"
        group_list.append(f"Tên nhóm: {group_name}\nID nhóm: {group_id}\nTrạng thái: {status}\n")

    if not group_list:
        success_message = "• Bạn không có nhóm nào để hiển thị."
    else:
        success_message = "[ DANH SÁCH NHÓM ]\n\n" + "\n".join(
            f"{i + 1}.\n{group_info}" for i, group_info in enumerate(group_list)
        )
    
    max_message_length = 3000
    if len(success_message) <= max_message_length:
        client.replyMessage(Message(text=success_message, style=styles), message_object, thread_id, thread_type)
    else:
        parts = [success_message[i:i+max_message_length] for i in range(0, len(success_message), max_message_length)]
        for part in parts:
           client.replyMessage(Message(text=part, style=styles), message_object, thread_id, thread_type)
        
def ft_vxkiue():
    return {
        'lgr': handle_lgr_command
    }
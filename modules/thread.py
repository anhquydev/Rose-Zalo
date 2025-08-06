import json
import os
import time
from zlapi.models import *
from config import ADMIN

def is_admin(author_id):
    return str(author_id) in ADMIN

des = {
    'version': "1.0.6",
    'credits': "Vũ Xuân Kiên",
    'description': "Duyệt nhóm, ban nhóm, duyệt id, ban id...",
    'power': "Quản trị viên Bot"
}

def handle_duyetbox_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        msg = "Bạn không có quyền sử dụng lệnh này."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000000000)
        return

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

def save_duyetbox_data(data):
    with open('modules/cache/duyetboxdata.json', 'w') as f:
        json.dump(data, f, indent=4)

def handle_duyetbox_command(message, message_object, thread_id, thread_type, author_id, client):
    group_info = client.fetchGroupInfo(thread_id)
    group_name = group_info.gridInfoMap.get(thread_id, {}).get('name', 'None')
    current_time = time.strftime("%H:%M:%S - %d/%m/%Y", time.localtime())

    text = message.split()
    if len(text) < 2:
        error_message = "Vui lòng nhập lệnh đầy đủ: `thread duyet`,\n `thread ban`,\n `thread duyetall`,\n `thread banall`,\n `thread listduyet`,\n `thread list-approved`,\n `thread banid`,\n `thread duyetid`"
        client.sendMessage(Message(text=error_message), thread_id, thread_type)
        return

    action = text[1].lower()
    data = load_duyetbox_data()
    
    if action == "duyet":
        if thread_id not in data:
            data.append(thread_id)
            save_duyetbox_data(data)
            success_message = f"• Đã duyệt nhóm thành công\n• Nhóm: {group_name}\n• ID nhóm: {thread_id}\n• Vào lúc: {current_time}."
        else:
            success_message = "• Nhóm này đã được duyệt trước đó."

    elif action == "duyetid" and len(text) > 2:
        target_group_id = text[2]
        if target_group_id not in data:
            data.append(target_group_id)
            save_duyetbox_data(data)
            target_group_name = client.fetchGroupInfo(target_group_id).gridInfoMap.get(target_group_id, {}).get('name', 'None')
            success_message = f"• Đã duyệt nhóm với ID {target_group_id} thành công\n• Nhóm: {target_group_name}\n• Vào lúc: {current_time}."
            gui = Message(text="Nhóm của bạn đã được ADMIN(Vũ Xuân Kiên) duyệt từ xa")
            client.sendMessage(gui, thread_id=target_group_id, thread_type=ThreadType.GROUP)
        else:
            success_message = f"• Nhóm với ID {target_group_id} đã được duyệt trước đó."
    
    elif action == "ban":
        if thread_id in data:
            data.remove(thread_id)
            save_duyetbox_data(data)
            success_message = f"• Ban nhóm thành công khỏi danh sách duyệt\n• Nhóm: {group_name}\n• ID nhóm: {thread_id}\n• Vào lúc: {current_time}."
        else:
            success_message = "• Nhóm này chưa được duyệt, không thể ban."

    elif action == "banid" and len(text) > 2:
        target_group_id = text[2]
        if target_group_id in data:
            data.remove(target_group_id)
            save_duyetbox_data(data)
            target_group_name = client.fetchGroupInfo(target_group_id).gridInfoMap.get(target_group_id, {}).get('name', 'None')
            success_message = f"• Đã ban nhóm với ID {target_group_id} thành công\n• Nhóm: {target_group_name}\n• Vào lúc: {current_time}."
            gui = Message(text="Nhóm của bạn đã được ADMIN(Vũ Xuân Kiên) ban từ xa")
            client.sendMessage(gui, thread_id=target_group_id, thread_type=ThreadType.GROUP)
        else:
            success_message = f"• Nhóm với ID {target_group_id} chưa được duyệt, không thể ban."

    elif action == "duyetall":
        all_group_ids = list(client.fetchAllGroups().gridVerMap.keys())
        newly_approved_groups = [group_id for group_id in all_group_ids if group_id not in data]
        data.extend(newly_approved_groups)
        save_duyetbox_data(data)
        group_list = "> Đã duyệt thành công toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(newly_approved_groups)
        )
        success_message = group_list if newly_approved_groups else "Tất cả các nhóm đã được duyệt."

    elif action == "banall":
        banned_groups = [group_id for group_id in data]
        data.clear()
        save_duyetbox_data(data)
        group_list = "> Đã ban thành công toàn bộ nhóm:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(banned_groups)
        )
        success_message = group_list if banned_groups else "Không có nhóm nào trong danh sách duyệt để ban."

    elif action == "listduyet":
        approved_groups = [group_id for group_id in data]
        group_list = "> Danh sách nhóm đã duyệt:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(approved_groups)
        )
        success_message = group_list if approved_groups else "Không có nhóm nào được duyệt."

    elif action == "list-approved":
        all_group_ids = list(client.fetchAllGroups().gridVerMap.keys())
        unapproved_groups = [group_id for group_id in all_group_ids if group_id not in data]
        group_list = "> Các nhóm chưa được duyệt:\n" + "\n".join(
            f"{i+1}:\n• Tên nhóm: {client.fetchGroupInfo(group_id).gridInfoMap.get(group_id, {}).get('name', 'None')}\n• ID: {group_id}"
            for i, group_id in enumerate(unapproved_groups)
        )
        success_message = group_list if unapproved_groups else "Tất cả các nhóm đã được duyệt."
    
    else:
        success_message = "• Vui lòng nhập lệnh đầy đủ: `thread duyet`,\n `thread ban`,\n `thread duyetall`,\n `thread banall`,\n `thread listduyet`,\n `thread list-approved`,\n `thread banid`,\n `thread duyetid`"

    client.replyMessage(Message(text=success_message), message_object, thread_id, thread_type, ttl=900000)

def ft_vxkiue():
    return {
        'thread': handle_duyetbox_command
    }

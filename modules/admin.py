import json
from zlapi.models import Message
from config import ADMIN

des = {
    'version': "1.0.7",
    'credits': "Nguyễn Đức Tài",
    'description': "Quản lý danh sách admin",
    'power': "Quản trị viên Bot"
}

def is_primary_admin(author_id):
    with open('seting.json', 'r') as f:
        data = json.load(f)
    return author_id == data.get('admin')

def is_secondary_admin(author_id):
    with open('seting.json', 'r') as f:
        data = json.load(f)
    return author_id in data.get('adm', [])

def is_admin(author_id):
    return is_primary_admin(author_id) or is_secondary_admin(author_id)

def add_admin(uids, client):
    with open('seting.json', 'r') as f:
        data = json.load(f)
    
    added_users = []
    for uid in uids:
        if uid not in data.get('adm', []):
            data.setdefault('adm', []).append(uid)
            author_info = client.fetchUserInfo(uid).changed_profiles.get(uid, {})
            name = author_info.get('zaloName', 'Không xác định')
            added_users.append(f"• Đã thêm {name} vào danh sách admin bot")

    with open('seting.json', 'w') as f:
        json.dump(data, f, indent=4)

    if added_users:
        return "\n".join(added_users)
    else:
        return "• Không có admin mới nào được thêm."

def remove_admin(uids, client):
    with open('seting.json', 'r') as f:
        data = json.load(f)

    removed_users = []
    for uid in uids:
        if uid in data.get('adm', []):
            data.get('adm', []).remove(uid)
            author_info = client.fetchUserInfo(uid).changed_profiles.get(uid, {})
            name = author_info.get('zaloName', 'Không xác định')
            removed_users.append(f"• Đã xoá {name} khỏi danh sách admin bot")

    with open('seting.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    if removed_users:
        return "\n".join(removed_users)
    else:
        return "• Không có admin nào bị xóa."

def list_admins(client):
    with open('seting.json', 'r') as f:
        data = json.load(f)
    
    qtv_bot = data.get('admin')
    qtv_c2 = data.get('adm', [])
    
    if not qtv_bot and not qtv_c2:
        return "• Danh sách admin bot trống."
    
    admin_text = "[ LIST ADMIN VXK ZALO BOT ]\n\n"

    if qtv_bot:
        primary_author_info = client.fetchUserInfo(qtv_bot).changed_profiles.get(qtv_bot, {})
        qtvbot_name = primary_author_info.get('zaloName', 'Không xác định')
        admin_text += f"• Primary Admin:\n   • Name: {qtvbot_name}\n   • ID: {qtv_bot}\n\n"

    if qtv_c2:
        admin_text += "• Secondary Admins:\n"
        number_mapping = {
            1: '➊', 2: '➋', 3: '➌', 4: '➍', 5: '➎',
            6: '➏', 7: '➐', 8: '➑', 9: '➒', 10: '➓'
        }
        for idx, uid in enumerate(qtv_c2, 1):
            author_info = client.fetchUserInfo(uid).changed_profiles.get(uid, {})
            author_name = author_info.get('zaloName', 'Không xác định')
            formatted_index = number_mapping.get(idx, str(idx))
            admin_text += f"  {formatted_index}:\n   • Name: {author_name}\n   • ID: {uid}\n\n"
    return admin_text

def handle_admin_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        response_message = "• Bạn không đủ quyền hạn để sử dụng lệnh này."
        message_to_send = Message(text=response_message)
        client.replyMessage(message_to_send, message_object, thread_id, thread_type)
        return

    text = message.split()
    if len(text) < 2:
        error_message = Message(text="• Vui lòng nhập lệnh hợp lệ.\n• add <@tag1> <@tag2>...\n• remove <@tag1> <@tag2>...\n• list")
        client.sendMessage(error_message, thread_id, thread_type)
        return

    subcommand = text[1].lower()
    if subcommand == "add" and message_object.mentions:
        uids = [mention['uid'] for mention in message_object.mentions]
        response_message = add_admin(uids, client)

    elif subcommand == "remove" and message_object.mentions:
        uids = [mention['uid'] for mention in message_object.mentions]
        response_message = remove_admin(uids, client)

    elif subcommand == "list":
        response_message = list_admins(client)

    else:
        response_message = "• Lệnh không hợp lệ. Vui lòng sử dụng: admin add <@tag>, admin remove <@tag> hoặc adm list."

    message_to_send = Message(text=response_message)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'admin': handle_admin_command
    }
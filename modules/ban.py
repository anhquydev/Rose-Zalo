from zlapi.models import Message
from config import ADMIN
ADMIN_ID = ADMIN

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Block thành viên trong nhóm",
    'power': "Quản trị viên Bot / Quản trị viên Nhóm"
}

def handle_ban_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "• Bạn không có quyền sử dụng lệnh này."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return

    user_ids_to_ban = []
    if message_object.mentions:
        user_ids_to_ban.extend([mention.uid for mention in message_object.mentions])
    elif message_object.quote:
        user_ids_to_ban.append(str(message_object.quote.ownerId))

    if not user_ids_to_ban:
        msg = "• Tag một hoặc nhiều người cần Block."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return
    
    group_data = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
    admins = group_data.adminIds
    owners = group_data.creatorId

    if client.uid not in admins and client.uid != owners:
        msg = "• Bot không có quyền quản trị."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return

    baned_names = []
    for user_id in user_ids_to_ban:
        if user_id in admins or user_id == owners:
            if user_id in admins:
                msg = f"• Bot không thể Block key bạc."
            elif user_id == owners:
                msg = f"• Bot không thể Block key vàng."
            client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=86400000)
            continue
        
        user_info = client.fetchUserInfo(user_id)
        user_name = user_info.changed_profiles[user_id].zaloName
        client.blockUsersInGroup(user_id, thread_id)
        baned_names.append(user_name)

    if baned_names:
        msg = f"• Đã Block {', '.join(baned_names)} Khỏi Nhóm."
        client.send(Message(text=msg), thread_id, thread_type, ttl=60000)
    

def ft_vxkiue():
    return {
        'ban': handle_ban_command
    }
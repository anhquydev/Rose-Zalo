from zlapi.models import Message
from config import ADMIN
ADMIN_ID = ADMIN

des = {
    'version': "1.0.1",
    'credits': "Quốc Khánh",
    'description': "Kick thành viên trong nhóm",
    'power': "Quản trị viên Bot / Quản trị viên Nhóm"
}

def handle_kick_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "🚫 Sếp ơi, có thèn đòi dùng lệnh sếp :33"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return

    user_ids_to_kick = []
    if message_object.mentions:
        user_ids_to_kick.extend([mention.uid for mention in message_object.mentions])
    elif message_object.quote:
        user_ids_to_kick.append(str(message_object.quote.ownerId))

    if not user_ids_to_kick:
        msg = "Nhập như vầy nè Sếp :D\nkick [reply] or @user1 @user2 `✅`"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=86400000)
        return
    
    group_data = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
    admins = group_data.adminIds
    owners = group_data.creatorId

    if client.uid not in admins and client.uid != owners:
        msg = "Đưa Em Key Bạc 🗝️, Em Kick Cho Sếp Xem :D"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=86400000)
        return

    kicked_names = []
    for user_id in user_ids_to_kick:
        if user_id in admins or user_id == owners:
            if user_id in admins:
                msg = f"Thưa Sếp, em không thể kick key bạc của nhóm! 🚫"
            elif user_id == owners:
                msg = f"Thưa Sếp, em không thể kick key vàng của nhóm! 🚫"
            client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=86400000)
            continue
        
        user_info = client.fetchUserInfo(user_id)
        user_name = user_info.changed_profiles[user_id].zaloName
        client.kickUsersInGroup(user_id, thread_id)
        kicked_names.append(user_name)

    if kicked_names:
        msg = f"Báo Sếp, đã đá {', '.join(kicked_names)} khỏi nhóm. ✅"
        client.send(Message(text=msg), thread_id, thread_type, ttl=86400000)
    

def ft_vxkiue():
    return {
        'kick': handle_kick_command
    }
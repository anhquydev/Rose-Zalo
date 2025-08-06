import json
import os
from zlapi.models import Message, Mention
from config import ADMIN

ADMIN_ID = ADMIN
mute_vxk = "data/khoamom.json"

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Mute những thành viên gây phiền phức",
    'power': "Quản trị viên Bot"
}

def load_mute_list():
    if os.path.exists(mute_vxk):
      with open(mute_vxk, 'r') as f:
        return json.load(f)
    return {}

def save_mute_list(data):
    with open(mute_vxk, 'w') as f:
      json.dump(data, f, indent=4)

def handle_mute_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "🚫 Sếp ơi, có thèn đòi dùng lệnh sếp :33"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return

    user_id = None
    if message_object.mentions:
        user_id = str(message_object.mentions[0].uid)
    elif message_object.quote:
        user_id = str(message_object.quote.ownerId)

    if not user_id:
        msg = "Nhập Như Vầy Nè Sếp: !mute @user `✅`"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=12000)
        client.sendReaction(message_object, "✅", thread_id, thread_type)
        return

    mute_list = load_mute_list()
    if thread_id not in mute_list:
        mute_list[thread_id] = []

    if user_id in mute_list[thread_id]:
        msg = f"Thèn này @mention đã có trong danh sách mute rồi Sếp! 🚫"
        mention = Mention(user_id, offset=9, length=8)
    else:
        mute_list[thread_id].append(user_id)
        msg = f"Đã thêm @mention thèn này vào danh sách mute. ✅"
        offset_mention = msg.find("@mention")
        mention = Mention(user_id, offset=offset_mention, length=8)

    save_mute_list(mute_list)
    client.replyMessage(Message(text=msg, mention=mention), message_object, thread_id, thread_type, ttl=12000)
    client.sendReaction(message_object, "✅ Anh Quý đẹp trai", thread_id, thread_type)

def handle_unmute_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "🚫 Sếp ơi, có thèn đòi dùng lệnh sếp :33\n\nLiên Hệ Sếp Tôi Nếu Muốn Sử Dụng Bot:"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        client.sendBusinessCard(userId=790318026347075757, qrCodeUrl=client.fetchUserInfo(client.uid).changed_profiles[client.uid]['avatarUrl'], phone="Cảm ơn vì đã đến!", thread_id=thread_id, thread_type=thread_type)
        client.sendReaction(message_object, "🚫", thread_id, thread_type)
        return

    if message_object.mentions:
        user_id = str(message_object.mentions[0].uid)
    elif message_object.quote:
        user_id = str(message_object.quote.ownerId)
    else:
        msg = "Nhập Như Vầy Nè Sếp: !unmute @user `✅`"
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=12000)
        client.sendReaction(message_object, "✅ Sai kìa sếp", thread_id, thread_type)
        return

    mute_list = load_mute_list()
    if thread_id not in mute_list:
        mute_list[thread_id] = []

    if user_id not in mute_list[thread_id]:
        msg = f"Báo Sếp, @mention thèn này không có trong danh sách mute! 🚫"
        mention = Mention(user_id, offset=9, length=8)
    else:
        mute_list[thread_id].remove(user_id)
        msg = f"Đã xoá @mention thèn này khỏi danh sách mute. ✅"
        offset_mention = msg.find("@mention")
        mention = Mention(user_id, offset=offset_mention, length=8)
    
    save_mute_list(mute_list)
    client.replyMessage(Message(text=msg, mention=mention), message_object, thread_id, thread_type, ttl=12000)
    client.sendReaction(message_object, "✅ Anh Quý đẹp trai ", thread_id, thread_type)

def ft_vxkiue():
    return {
        'mute': handle_mute_command,
        'unmute': handle_unmute_command
    }
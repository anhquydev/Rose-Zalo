from zlapi.models import Message, MultiMsgStyle, MessageStyle
from config import PREFIX
from config import ADMIN
ADMIN_ID = ADMIN

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Xoá tin nhắn người dùng",
    'power': "Quản trị viên Bot"
}

def handle_del_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "• Bạn không có quyền sử dụng lệnh này."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=12000)
        return

    if not message_object.quote:
        msg = f"• Reply tin nhắn cần xóa."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=12000)
        return

    msg2del = message_object.quote

    try:
        client.deleteGroupMsg(msg2del.globalMsgId, msg2del.ownerId, msg2del.cliMsgId, thread_id)
    except Exception:
        pass


def ft_vxkiue():
    return {
        'del': handle_del_command
    }
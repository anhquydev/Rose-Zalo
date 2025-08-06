from zlapi.models import Message, ZaloAPIException
from config import ADMIN, IMEI
import time

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh rời nhóm",
    'power': "Vũ Xuân Kiên"
}

def handle_leave_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "Bạn không có quyền sử dụng lệnh này!"
        styles = MultiMsgStyle([
                MessageStyle(offset=0, length=10000, style="font", size="10", auto_format=False),
            ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=86400000)
        return
    try:
        client.leaveGroup(thread_id, imei=IMEI)
        
    except ZaloAPIException as e:
        msg = f"err: {e}"
        styles = MultiMsgStyle([
                MessageStyle(offset=0, length=10000, style="font", size="10", auto_format=False),
            ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=86400000)
    except Exception as e:
        msg = f"error: {e}"
        styles = MultiMsgStyle([
                MessageStyle(offset=0, length=10000, style="font", size="10", auto_format=False),
            ])
        client.replyMessage(Message(text=msg, style=styles), message_object, thread_id, thread_type, ttl=86400000)

def ft_vxkiue():
    return {
        'leave': handle_leave_command
    }

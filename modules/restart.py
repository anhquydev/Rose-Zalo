import sys, os
from config import ADMIN
from zlapi.models import Message, MultiMsgStyle, MessageStyle

ADMIN_ID = ADMIN

des = {
    'version': "1.0.0",
    'credits': "Đức Tài",
    'description': "Restart lại bot",
    'power': "Quản trị viên Bot"
}

def is_admin(author_id):
    return author_id == ADMIN_ID

def handle_reset_command(message, message_object, thread_id, thread_type, author_id, client):
    if not is_admin(author_id):
        noquyen = "Bạn không có quyền để thực hiện điều này!"
        client.replyMessage(Message(text=noquyen), message_object, thread_id, thread_type)
        return
    
    try:
        action = "✅"
        client.sendReaction(message_object, action, thread_id, thread_type, reactionType=75)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    except Exception as e:
        error_msg = f"Lỗi xảy ra khi restart bot: {str(e)}"
        client.replyMessage(Message(text=error_msg), message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'restart': handle_reset_command
    }

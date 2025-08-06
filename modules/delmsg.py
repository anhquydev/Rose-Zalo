from zlapi.models import *
from zlapi import Message, ThreadType
from config import PREFIX
from config import ADMIN

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Xoá tin nhắn người dùng theo số lượng",
    'power': "Quản trị viên Bot"
}

def handle_go_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        msg = "• Bạn không có quyền sử dụng lệnh này."
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=60000)
        return

    try:
        parts = message.split()
        if len(parts) < 2:
            client.replyMessage(Message(text="• Vui lòng nhập số lượng tin nhắn muốn xóa."), message_object, thread_id, thread_type)
            return
        num_to_delete = int(parts[1])
        if num_to_delete <= 0:
            client.replyMessage(Message(text="• Số lượng tin nhắn phải lớn hơn 0."), message_object, thread_id, thread_type)
            return
    except ValueError:
        client.replyMessage(Message(text="• Số lượng tin nhắn không hợp lệ. Vui lòng nhập một số."), message_object, thread_id, thread_type)
        return
    
    try:
        group_data = client.getRecentGroup(thread_id)
        if not group_data or not hasattr(group_data, 'groupMsgs'):
            client.replyMessage(Message(text="• Không có tin nhắn nào để xóa!"), message_object, thread_id, thread_type)
            return
        messages_to_delete = group_data.groupMsgs
        if not messages_to_delete:
            client.replyMessage(Message(text="• Không có tin nhắn nào để xóa!"), message_object, thread_id, thread_type)
            return

    except Exception as e:
        client.replyMessage(Message(text=f"• Lỗi khi lấy tin nhắn: {str(e)}"), message_object, thread_id, thread_type)
        return
    
    if len(messages_to_delete) < num_to_delete:
        num_to_delete = len(messages_to_delete)
        
    deleted_count = 0
    failed_count = 0
    for i in range(num_to_delete):
        msg = messages_to_delete[-(i + 1)]
        user_id = str(msg['uidFrom']) if msg['uidFrom'] != '0' else author_id
        try:
            deleted_msg = client.deleteGroupMsg(msg['msgId'], user_id, msg['cliMsgId'], thread_id)
            if deleted_msg.status == 0:
                deleted_count += 1
            else:
                failed_count += 1
        except Exception as e:
            failed_count += 1
            continue

    if failed_count > 0:
        client.replyMessage(
            Message(text=f"• Đã xóa {deleted_count} tin nhắn. Không thể xóa {failed_count} tin nhắn."),
            message_object, thread_id, thread_type
        )
    else:
        client.replyMessage(Message(text=f"• Đã xóa {deleted_count} tin nhắn thành công!"), message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'delmsg': handle_go_command
    }
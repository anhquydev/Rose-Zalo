import time
from zlapi.models import Message, MultiMsgStyle, MessageStyle
from config import ADMIN

des = {
    'version': "1.0.5",
    'credits': "Vũ Xuân Kiên",
    'description': "Gửi spam công việc cho người dùng được tag, cả group và tin nhắn riêng",
    'power': "Quản trị viên Bot"
}

def handle_spamtodo_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        client.replyMessage(
            Message(
                text="Bạn không có quyền sử dụng lệnh này.",
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len("Bạn không có quyền sử dụng lệnh này."), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len("Bạn không có quyền sử dụng lệnh này."), style="bold", auto_format=False)
                ])
            ),
            message_object, thread_id, thread_type
        )
        return

    parts = message.split(' ', 2)
    if len(parts) < 3:
        client.replyMessage(
            Message(
                text="Vui lòng cung cấp lệnh và nội dung và số lần spam công việc. \nForm: todo `all` hoặc `@mention` <công việc> <số lần>",
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len("Vui lòng cung cấp lệnh và nội dung và số lần spam công việc. \nForm: todo `all` hoặc `@mention` <công việc> <số lần>"), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len("Vui lòng cung cấp lệnh và nội dung và số lần spam công việc. \nForm: todo `all` hoặc `@mention` <công việc> <số lần>"), style="bold", auto_format=False)
                ])
            ),
            message_object, thread_id, thread_type
        )
        return

    try:
        content_and_count = parts[2]
        content, num_repeats_str = content_and_count.rsplit(' ', 1)
        num_repeats = int(num_repeats_str)
    except ValueError:
        client.replyMessage(
            Message(
                text="Số lần phải là một số nguyên.",
                style=MultiMsgStyle([
                    MessageStyle(offset=0, length=len("Số lần phải là một số nguyên."), style="font", size=13, auto_format=False),
                    MessageStyle(offset=0, length=len("Số lần phải là một số nguyên."), style="bold", auto_format=False)
                ])
            ),
            message_object, thread_id, thread_type
        )
        return

    if "all" in message.lower():
        try:
            group_info = client.fetchGroupInfo(thread_id)
            if not group_info or not hasattr(group_info, 'gridInfoMap'):
                raise ValueError("Không tìm thấy thông tin nhóm.")

            group_data = group_info.gridInfoMap.get(str(thread_id))
            if not group_data or not group_data.get('memVerList'):
                raise ValueError("Danh sách thành viên nhóm không tồn tại hoặc rỗng.")

            group_members = [
                mem.split('_')[0] for mem in group_data['memVerList']
                if mem.split('_')[0] != author_id
            ]
            if not group_members:
                raise ValueError("Không có thành viên nào trong danh sách.")

        except Exception as e:
            client.replyMessage(
                Message(
                    text=f"Không thể lấy danh sách thành viên nhóm: {str(e)}",
                    style=MultiMsgStyle([
                        MessageStyle(offset=0, length=len(f"Không thể lấy danh sách thành viên nhóm: {str(e)}"), style="font", size=13, auto_format=False),
                        MessageStyle(offset=0, length=len(f"Không thể lấy danh sách thành viên nhóm: {str(e)}"), style="bold", auto_format=False)
                    ])
                ),
                message_object, thread_id, thread_type
            )
            return
    else:
        group_members = [mention['uid'] for mention in message_object.mentions]

        if not group_members:
            client.replyMessage(
                Message(
                    text="Vui lòng tag người dùng để giao công việc.",
                    style=MultiMsgStyle([
                        MessageStyle(offset=0, length=len("Vui lòng tag người dùng để giao công việc."), style="font", size=13, auto_format=False),
                        MessageStyle(offset=0, length=len("Vui lòng tag người dùng để giao công việc."), style="bold", auto_format=False)
                    ])
                ),
                message_object, thread_id, thread_type
            )
            return
    recipient = 'all' if 'all' in message.lower() else ', '.join([f'{mem}' for mem in group_members])
    result_msg = f"[ XUAN KIEN PROJECT ]\n" \
                 f"Người nhận: {recipient}\n" \
                 f"Nội dung: {content}\n" \
                 f"Số lần: {num_repeats}\n" \
                 f"Tiến hành SPAM Todo!"

    result_msg_length = len(result_msg)
    client.replyMessage(
        Message(
            text=result_msg,
            style=MultiMsgStyle([
                MessageStyle(offset=0, length=result_msg_length, style="font", size=13, auto_format=False),
                MessageStyle(offset=0, length=result_msg_length, style="bold", auto_format=False)
            ])
        ),
        message_object, thread_id, thread_type
    )

    for i in range(num_repeats):
        for member_id in group_members:
            client.sendToDo(
                message_object=message_object,
                content=content,
                assignees=[member_id],
                thread_id=thread_id,
                thread_type=thread_type,
                due_date=-1,
                description="ft. Vxkiue"
            )
            client.sendToDo(
            message_object=message_object,
            content=content,
            assignees=[member_id],
            thread_id=member_id,
            thread_type=ThreadType.USER,
            due_date=-1,
            description="ft. Vxkiue"
        )
 

def ft_vxkiue():
    return {
        'todo': handle_spamtodo_command
    }

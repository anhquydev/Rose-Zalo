from zlapi.models import Message, ThreadType
import os

des = {
    'version': "1.0.5",
    'credits': "Vũ Xuân Kiên",
    'description': "Gửi tin nhắn riêng đến người dùng",
    'power': "Quản trị viên Bot"
}

def handle_sendmsg_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if '&&' not in message or not message_object.mentions:
            client.send(
                Message(text="• Sử dụng: sendmsg <@user>&&<nội dung>"),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        user_part, content_source = map(str.strip, message.split(' &&', 1))
        if not content_source:
            client.send(
                Message(text="• Vui lòng nhập nội dung tin nhắn sau '&&'."),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        user_id = message_object.mentions[0]['uid']
        if content_source.lower() == 'auto':
            try:
                with open("noidung.txt", "r", encoding="utf-8") as file:
                    content = file.read().strip()
                    if not content:
                        client.send(
                            Message(text="• Tệp noidung.txt rỗng. Vui lòng thêm nội dung."),
                            thread_id=thread_id,
                            thread_type=thread_type
                        )
                        return
            except FileNotFoundError:
                client.send(
                    Message(text="• Không tìm thấy file noidung.txt."),
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return
            except Exception as e:
                client.send(
                    Message(text=f"• Lỗi khi đọc file noidung.txt: {str(e)}"),
                    thread_id=thread_id,
                    thread_type=thread_type
                )
                return
        else:
            content = content_source

        repeat_count = 1
        if content_source.lower() == 'auto':
            repeat_count = 100

        for _ in range(repeat_count):
            client.send(
                Message(text=content),
                thread_id=user_id,
                thread_type=ThreadType.USER
            )
        client.sendReaction(message_object, "✅", thread_id, thread_type, reactionType=75)
    except Exception as e:
        error_message = f"Lỗi khi thực hiện lệnh sendmsg: {str(e)}"
        client.send(
            Message(text=error_message),
            thread_id=thread_id,
            thread_type=thread_type
        )

def ft_vxkiue():
    return {
        'sendmsg': handle_sendmsg_command
    }
    
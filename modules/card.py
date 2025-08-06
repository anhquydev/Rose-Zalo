from zlapi.models import Message, ThreadType

des = {
    'version': "1.0.4",
    'credits': "Vũ Xuân Kiên",
    'description': "Tạo card thông tin người dùng",
    'power': "Thành viên"
}

def handle_cardinfo_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        if ' &&' not in message or not message_object.mentions:
            client.send(
                Message(text="• Sử dụng <@user> && <content>"),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
            
        user_part, phone_content = map(str.strip, message.split(' &&', 1))
        if not phone_content:
            client.send(
                Message(text="• Vui lòng nhập nội dung sau '&&'."),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        userId = message_object.mentions[0]['uid']
        user_info = client.fetchUserInfo(userId).changed_profiles.get(userId)
        if not user_info:
            client.send(
                Message(text="• Không thể lấy thông tin người dùng."),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return

        avatarUrl = user_info.avatar
        if not avatarUrl:
            client.send(
                Message(text="• Người dùng này không có ảnh đại diện."),
                thread_id=thread_id,
                thread_type=thread_type
            )
            return
        client.sendBusinessCard(
            userId=userId,
            qrCodeUrl=avatarUrl,
            thread_id=thread_id,
            thread_type=thread_type,
            phone=phone_content
        )
    except Exception as e:
        error_message = f"• Lỗi khi thực hiện lệnh card: {str(e)}"
        client.send(
            Message(text=error_message),
            thread_id=thread_id,
            thread_type=thread_type
        )

def ft_vxkiue():
    return {
        'card': handle_cardinfo_command
    }

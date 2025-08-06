from zlapi.models import Message

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Lấy link group zalo",
    'power': "Thành viên"
}

def handle_grouplink_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        nguthichet = client.getGroupLink(chatID=thread_id)
        print("Dữ liệu từ Zalo API:", nguthichet)
        if nguthichet.get("error_code") == 0:
            data = nguthichet.get("data")
            if isinstance(data, dict):
                if data.get('link'):
                    response_message = f"{data['link']}"
                elif data.get('url'):
                    response_message = f"{data['url']}"
                else:
                    response_message = f"Không tìm thấy link group. Dữ liệu trả về: {data}"
            elif isinstance(data, str):
                response_message = f"{data}"
            else:
                response_message = f"Không tìm thấy link group."
        else:
            response_message = f"Lỗi từ Zalo API: {nguthichet.get('error_message', 'Lỗi không xác định')}"
    except ValueError as e:
        response_message = f"Lỗi: Cần có Group ID."
    except Exception as e:
        response_message = f"Đã xảy ra lỗi: {str(e)}"

    message_to_send = Message(text=response_message)
    client.replyMessage(message_to_send, message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'grouplink': handle_grouplink_command
    }

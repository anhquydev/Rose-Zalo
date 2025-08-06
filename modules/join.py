from zlapi.models import Message, ZaloAPIException, ThreadType, Mention, MultiMention
from config import ADMIN
import time

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh tham gia nhóm",
    'power': "Quản trị viên Bot"
}

def handle_join_command(message, message_object, thread_id, thread_type, author_id, client):
    print(f"[DEBUG] Nhận lệnh từ: {author_id}, Nội dung: {message}")
    
    if author_id not in ADMIN:
        print("[DEBUG] Người dùng không có quyền sử dụng lệnh này.")
        client.replyMessage(Message(text="Quyền lồn biên giới."), message_object, thread_id, thread_type, ttl=60000)
        return

    try:
        parts = message.split(" ", 1)
        if len(parts) < 2:
            print("[DEBUG] Không có link nhóm trong lệnh.")
            client.replyMessage(Message(text="Link đâu? Đùa bố à"), message_object, thread_id, thread_type, ttl=86400000)
            return

        group_link = parts[1].strip()
        print(f"[DEBUG] Link nhóm nhận được: {group_link}")

        if not group_link.startswith("https://zalo.me/"):
            print("[DEBUG] Link nhóm không hợp lệ.")
            client.replyMessage(Message(text="Cái địt bà m"), message_object, thread_id, thread_type, ttl=86400000)
            return

        print("[DEBUG] Đang gửi yêu cầu tham gia nhóm...")
        data_join = client.joinGroup(group_link)
        print(f"[DEBUG] Phản hồi từ joinGroup: {data_join}")

        if data_join:
            if 'error_code' in data_join:
                error_code = data_join['error_code']
                msg_err = {
                    0: "Rồi đó con",
                    240: "Duyệt bố đi con",
                    178: "Bố m là thành viên r còn join ăn c à",
                    227: "Nhóm với link có tồn tại đéo đâu ???",
                    175: "Con chó nào nó block r",
                    1003: "Nhóm full mem cmnr",
                    1004: "Giới hạn mem cmnr",
                    1022: "Yc tham gia trước đó r"
                }
                msg = msg_err.get(error_code, f"Lỗi: {data_join}")
            else:
                msg = f"{data_join}"
        else:
            msg = "Lỗi"

        print(f"[DEBUG] Tin nhắn phản hồi khi tham gia nhóm: {msg}")
        client.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=86400000)

        print("[DEBUG] Đang lấy ID và thông tin nhóm từ link...")
        group_info_response = client.getIDsGroup(group_link)
        print(f"[DEBUG] Phản hồi từ getIDsGroup: {group_info_response}")

        if not group_info_response:
            print("[ERROR] API không trả về dữ liệu hoặc trả về None.")
            return

        if not isinstance(group_info_response, dict):
            print(f"[ERROR] API trả về kiểu dữ liệu không hợp lệ: {type(group_info_response)}")
            return

        group_id = group_info_response.get('groupId')
        print(f"[DEBUG] ID nhóm lấy được: {group_id}")

        if not group_id:
            print(f"[ERROR] Không tìm thấy 'groupId' trong phản hồi: {group_info_response}")
            return

        print("[DEBUG] Lấy danh sách quản trị viên nhóm...")
        admins = group_info_response.get('adminIds', [])
        creator_id = group_info_response.get('creatorId')
        if creator_id and creator_id not in admins:  # Đảm bảo creator không bị trùng lặp
            admins.append(creator_id)

        admins = list(set(admins))  # Loại bỏ trùng lặp
        print(f"[DEBUG] Danh sách admin: {admins}")

        if not admins:
            print("[WARNING] Không tìm thấy admin nào trong nhóm.")
            return

        text = "Vũ Xuân Kiên (Admin Vxk Zalo Bot) Tới Chơi "
        mentions = []
        offset = len(text)

        for admin_id in admins:
            mention = Mention(uid=admin_id, offset=offset, length=1, auto_format=False)
            mentions.append(mention)
            text += "@ "
            offset += 2

        multi_mention = MultiMention(mentions)

        print(f"[DEBUG] Tin nhắn sẽ gửi vào nhóm {group_id}: {text}")
        client.send(
            Message(text=text, mention=multi_mention),
            thread_id=group_id,
            thread_type=ThreadType.GROUP
        )
        print(f"[DEBUG] Đã gửi tin nhắn thành công tới nhóm {group_id}.")
    except ZaloAPIException as e:
        print(f"[ERROR] Zalo API Exception: {e}")
    except Exception as e:
        print(f"[ERROR] Lỗi không xác định: {e}")

def ft_vxkiue():
    return {
        'join': handle_join_command
    }
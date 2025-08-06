from zlapi.models import Message
from config import ADMIN

des = {
    'version': "1.0.0",
    'credits': "TRBAYK (NGSON)",
    'description': "Thay đổi cài đặt nhóm.",
    'power': "Quản trị viên Bot"
}

def send_error_message(client, thread_id, thread_type, message):
    error_message = Message(text=message)
    client.sendMessage(error_message, thread_id, thread_type)

def check_admin_permissions(author_id, creator_id, admin_ids):
    all_admin_ids = set(admin_ids)
    all_admin_ids.add(creator_id)
    all_admin_ids.update(ADMIN)
    return author_id in all_admin_ids

def validate_setting(setting):
    valid_settings = {
        "lockname": "blockName",
        "styleadmin": "signAdminMsg",
        "addmbonly": "addMemberOnly",
        "onlytopic": "setTopicOnly",
        "historymsg": "enableMsgHistory",
        "lockpost": "lockCreatePost",
        "lockpoll": "lockCreatePoll",
        "joinonly": "joinAppr",
        "lockchat": "lockSendMsg",
        "showmb": "lockViewMember"
    }
    return valid_settings.get(setting.lower())

def handle_block_name(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, blockName=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} tên nhóm thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_sign_admin_msg(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, signAdminMsg=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} ghi chú admin thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_add_member_only(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, addMemberOnly=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} chỉ cho phép thêm thành viên thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_set_topic_only(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, setTopicOnly=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} chỉ cho phép chủ đề thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_enable_msg_history(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, enableMsgHistory=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} lịch sử tin nhắn thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_lock_create_post(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, lockCreatePost=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} khóa tạo bài viết thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_lock_create_poll(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, lockCreatePoll=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} khóa tạo khảo sát thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_join_appr(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, joinAppr=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} yêu cầu gia nhập thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_lock_send_msg(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, lockSendMsg=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} khóa gửi tin nhắn thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_lock_view_member(action, thread_id, client):
    new_value = 1 if action == "on" else 0 if action == "off" else None
    if new_value is not None:
        client.changeGroupSetting(groupId=thread_id, lockViewMember=new_value)
        return f"Đã {'bật' if new_value == 1 else 'tắt'} khóa xem thành viên thành công."
    return "Hành động không hợp lệ. Vui lòng sử dụng 'on' hoặc 'off'."

def handle_group_setting_command(message, message_object, thread_id, thread_type, author_id, client):
    text = message.split()

    if len(text) < 3:
        error_message = Message(text="Vui lòng sử dụng cú pháp: stg <setting> <on/off>.\n\n"
                                      "Các cài đặt hợp lệ bao gồm:\n\n"
                                      "- lockname: Bật/tắt việc thay đổi tên nhóm.\n\n"
                                      "- styleadmin: Bật/tắt ghi chú admin trong tin nhắn.\n\n"
                                      "- addmbonly: Bật/tắt chế độ chỉ cho phép thêm thành viên.\n\n"
                                      "- onlytopic: Bật/tắt việc chỉ cho phép thay đổi chủ đề.\n\n"
                                      "- historymsg: Bật/tắt lịch sử tin nhắn trong nhóm.\n\n"
                                      "- lockpost: Bật/tắt việc khóa tạo bài viết.\n\n"
                                      "- lockpoll: Bật/tắt việc khóa tạo khảo sát.\n\n"
                                      "- joinonly: Bật/tắt yêu cầu phê duyệt khi gia nhập nhóm.\n\n"
                                      "- lockchat: Bật/tắt việc khóa gửi tin nhắn.\n\n"
                                      "- showmb: Bật/tắt việc khóa xem danh sách thành viên.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)
        return

    setting = text[1].lower()
    action = text[2].lower()

    group_info = client.fetchGroupInfo(thread_id)
    if not group_info or thread_id not in group_info.gridInfoMap:
        send_error_message(client, thread_id, thread_type, "Không thể lấy thông tin nhóm.")
        return

    group_data = group_info.gridInfoMap[thread_id]
    creator_id = group_data.get('creatorId')
    admin_ids = group_data.get('adminIds', [])

    if not check_admin_permissions(author_id, creator_id, admin_ids):
        send_error_message(client, thread_id, thread_type, "Chỉ key bạc, key vàng, admin mới có thể sử dụng.")
        return

    setting_action_map = {
        "lockname": handle_block_name,
        "styleadmin": handle_sign_admin_msg,
        "addmbonly": handle_add_member_only,
        "onlytopic": handle_set_topic_only,
        "historymsg": handle_enable_msg_history,
        "lockpost": handle_lock_create_post,
        "lockpoll": handle_lock_create_poll,
        "joinonly": handle_join_appr,
        "lockchat": handle_lock_send_msg,
        "showmb": handle_lock_view_member
    }

    setting_func = validate_setting(setting)
    if not setting_func:
        send_error_message(client, thread_id, thread_type, "Cài đặt không hợp lệ. Vui lòng sử dụng một trong các cài đặt sau: blockname, signadminmsg, addmemberonly, settopiconly, enablemsghistory, lockcreatepost, lockcreatepoll, joinappr, locksendmsg, lockviewmember.")
        return

    result_message = setting_action_map[setting](action, thread_id, client)
    send_error_message(client, thread_id, thread_type, result_message)

def ft_vxkiue():
    return {
        'stg': handle_group_setting_command
    }

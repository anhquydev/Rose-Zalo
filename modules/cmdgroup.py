from zlapi.models import Message, ZaloAPIException, Mention, MultiMention
from datetime import datetime
import json

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh quản lý nhóm",
    'power': "Mọi thành viên"
}

def handle_cmdgroup(message, message_object, thread_id, thread_type, author_id, client):
    try:
        parts = message.split(" ", 2)
        
        if len(parts) < 2:
            client.replyMessage(Message(text="Các lệnh hỗ trợ:\nfind - Tìm kiếm thành viên\nfindtag - Tag thành viên"), message_object, thread_id, thread_type, ttl=60000)
            return
        
        action = parts[1].lower()

        if action == "find":
            if len(parts) < 3:
                client.replyMessage(Message(text="Nhập tên thành viên cần tìm"), message_object, thread_id, thread_type, ttl=60000)
                return

            search_term = parts[2].strip().lower()

            group_link = "Không tìm thấy link."
            try:
                group_link_data = client.getGroupLink(chatID=thread_id)
                
                if group_link_data.get("error_code") == 0:
                    group_link = group_link_data.get("data", {}).get("link", group_link_data.get("data", {}).get("url", "Không có link"))
                elif group_link_data.get("error_code") == 227:
                    group_link = "Link nhóm không hợp lệ hoặc đã hết hạn."
                    client.replyMessage(Message(text="Đã xảy ra lỗi gì đó."), message_object, thread_id, thread_type, ttl=60000)
                    return
                else:
                    group_link = f"Đã xảy ra lỗi gì đó."
                    client.replyMessage(Message(text=group_link), message_object, thread_id, thread_type, ttl=60000)
                    return

            except Exception as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi gì đó."), message_object, thread_id, thread_type, ttl=60000)
                return


            try:
                members_data = client.getIDsGroup(group_link)

                if isinstance(members_data, dict) and "currentMems" in members_data and "name" in members_data:
                    members = members_data["currentMems"]
                    group_name = members_data["name"]
                else:
                    raise ValueError(f"Không thể lấy danh sách thành viên hoặc tên nhóm từ API. Phản hồi không hợp lệ: {members_data}")

            except Exception as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi gì đó. Lỗi lấy danh sách thành viên"), message_object, thread_id, thread_type, ttl=60000)
                return


            found_members = [
                {'dName': member['dName'], 'id': member['id']}
                for member in members if search_term in member['dName'].lower() or search_term in "".join([c[0] for c in member['dName'].split()]).lower()
            ]

            if found_members:
                response_text = f"🔎 Danh sách thành viên '{search_term}' tìm thấy hoặc có tên gần giống:\n\n"
                count = 0
                for member in found_members:
                    response_text += f"{count+1}.\n" 
                    response_text += f"- Tên: {member['dName']}, ID: {member['id']}\n\n"
                    count += 1
                    if count >= 100:
                        break
            else:
                response_text = f"Không tìm thấy thành viên nào có tên chứa '{search_term}'."
            
            client.replyMessage(Message(text=response_text), message_object, thread_id, thread_type, ttl=86400000)
        
        elif action == "findtag":
            if len(parts) < 3:
                client.replyMessage(Message(text="Nhập tên thành viên cần tag"), message_object, thread_id, thread_type, ttl=60000)
                return

            search_term = parts[2].strip().lower()

            group_link = "Không tìm thấy link."
            try:
                group_link_data = client.getGroupLink(chatID=thread_id)
                
                if group_link_data.get("error_code") == 0:
                    group_link = group_link_data.get("data", {}).get("link", group_link_data.get("data", {}).get("url", "Không có link"))
                elif group_link_data.get("error_code") == 227:
                    group_link = "Link nhóm không hợp lệ hoặc đã hết hạn."
                    client.replyMessage(Message(text="Đã xảy ra lỗi gì đó."), message_object, thread_id, thread_type, ttl=60000)
                    return
                else:
                    group_link = f"Đã xảy ra lỗi gì đó."
                    client.replyMessage(Message(text=group_link), message_object, thread_id, thread_type, ttl=60000)
                    return

            except Exception as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi gì đó."), message_object, thread_id, thread_type, ttl=60000)
                return

            try:
                members_data = client.getIDsGroup(group_link)

                if isinstance(members_data, dict) and "currentMems" in members_data and "name" in members_data:
                    members = members_data["currentMems"]
                    group_name = members_data["name"]
                else:
                    raise ValueError(f"Không thể lấy danh sách thành viên hoặc tên nhóm từ API. Phản hồi không hợp lệ: {members_data}")

            except Exception as e:
                client.replyMessage(Message(text=f"Đã xảy ra lỗi gì đó. Lỗi lấy danh sách thành viên"), message_object, thread_id, thread_type, ttl=60000)
                return

            found_members = [
                {'dName': member['dName'], 'id': member['id']}
                for member in members if search_term in member['dName'].lower() or search_term in "".join([c[0] for c in member['dName'].split()]).lower()
            ]

            if found_members:
                text = ""
                mentions = []
                offset = 0

                for member in found_members:
                    user_id = str(member['id'])
                    user_name = member['dName']

                    text += f"{user_name} "
                    mention = Mention(uid=user_id, offset=offset, length=len(user_name), auto_format=False)
                    mentions.append(mention)
                    offset += len(user_name) + 1

                multi_mention = MultiMention(mentions)

                client.replyMessage(Message(text=text, mention=multi_mention), message_object, thread_id, thread_type, ttl=86400000)
            else:
                client.replyMessage(Message(text=f"Không tìm thấy thành viên nào có tên chứa '{search_term}'."), message_object, thread_id, thread_type, ttl=86400000)

        else:
            client.replyMessage(Message(text="Commands Not Found."), message_object, thread_id, thread_type, ttl=60000)

    except ZaloAPIException as e:
        client.replyMessage(Message(text=f"Lỗi API: {e}"), message_object, thread_id, thread_type, ttl=86400000)
    except Exception as e:
        client.replyMessage(Message(text=f"Lỗi không xác định: {e}"), message_object, thread_id, thread_type, ttl=86400000)

def ft_vxkiue():
    return {
        'cmdgroup': handle_cmdgroup
    }
from zlapi.models import Message, ZaloAPIException, ThreadType, Mention, MultiMention
from config import ADMIN
import time
import random

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh spam nhóm bằng link",
    'power': "Quản trị viên Bot"
}

def load_spam_content(filename="noidung.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().splitlines()
            content = [line.strip() for line in content if line.strip()]
            return content
    except FileNotFoundError:
        print("Không tìm thấy file noidung.txt")
        return None
    except Exception as e:
        print(f"Lỗi đọc file nội dung: {e}")
        return None

def handle_spamgroup_command(message, message_object, thread_id, thread_type, author_id, client):
    if author_id not in ADMIN:
        client.replyMessage(Message(text="Quyền lồn biên giới."), message_object, thread_id, thread_type, ttl=60000)
        print("Người dùng không có quyền.")
        return

    try:
        parts = message.split(" ", 2)
        if len(parts) < 3:
            print("Sai cú pháp lệnh.")
            return

        group_link = parts[1].strip()
        num_spams = int(parts[2].strip())

        if not group_link.startswith("https://zalo.me/"):
            client.replyMessage(Message(text="Link sai định dạng"), message_object, thread_id, thread_type, ttl=86400000)
            print("Link nhóm sai định dạng.")
            return

        spam_contents = load_spam_content()
        if not spam_contents:
            print("Không có nội dung spam.")
            return

        try:
            client.joinGroup(group_link)
            print(f"Đã tham gia nhóm {group_link}")
        except Exception as e:
            print(f"Lỗi khi tham gia nhóm: {e}")
            return

        try:
            group_info_response = client.getIDsGroup(group_link)
            group_id = group_info_response['groupId']
            print(f"ID nhóm: {group_id}")
        except Exception as e:
            print(f"Lỗi khi lấy ID nhóm: {e}")
            return

        try:
            members = group_info_response.get('currentMems', [])
            if not members:
                print("Không có thành viên trong nhóm.")
                return

            admins = group_info_response.get('adminIds', [])
            print(f"Danh sách Admin: {admins}")

            for i in range(num_spams):
                random_spam_content = random.choice(spam_contents)
                num_mentions = min(1000, len(members))
                random_members = random.sample(members, num_mentions)

                text = f"<b>{random_spam_content} 𝕏𝕦𝕒𝕟𝕂𝕚𝕖𝕟 khong thich ua rain rain rain</b>"
                mentions = []
                offset = len(text)

                for member in random_members:
                    user_id = member.get('id')
                    user_name = member.get('dName')
                    if not user_id or not user_name:
                        print("Thiếu thông tin user_id hoặc user_name, bỏ qua thành viên này.")
                        continue

                    mention = Mention(uid=user_id, offset=offset, length=len(user_name) + 1, auto_format=False)
                    mentions.append(mention)
                    offset = len(text)

                multi_mention = MultiMention(mentions)

                try:
                    client.send(
                        Message(text=text, mention=multi_mention, parse_mode="HTML"),
                        thread_id=group_id,
                        thread_type=ThreadType.GROUP
                    )
                    time.sleep(1)
                    print(f"Send Message Success: {text}")
                except Exception as e:
                    print(f"Lỗi khi gửi tin nhắn: {e}")


        except Exception as e:
            print(f"Lỗi tổng quan: {e}")
            pass

    except ZaloAPIException as e:
        print(f"Lỗi Zalo API: {e}")
        pass
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        pass

def ft_vxkiue():
    return {
        'spamgroup': handle_spamgroup_command
    }
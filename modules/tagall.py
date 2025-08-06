from zlapi.models import Message, ZaloAPIException, ThreadType, Mention, MultiMention
from config import ADMIN
import time
import random

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh tagall nhóm",
    'power': "Quản trị viên Bot"
}


def handle_tagall_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        parts = message.split(" ", 1)
        if len(parts) < 2:
            return

        tagall_message = parts[1].strip()

        try:
            group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
            members = group_info.get('memVerList', [])
            if not members:
                return
            
            text = f"<b>{tagall_message}</b>"
            mentions = []
            offset = len(text)
            
            for member in members:
                member_parts = member.split('_', 1)
                if len(member_parts) != 2:
                    continue
                user_id, user_name = member_parts
                mention = Mention(uid=user_id, offset=offset, length=len(user_name) + 1, auto_format=False)
                mentions.append(mention)
                offset += len(user_name) + 2

            multi_mention = MultiMention(mentions)

            try:
                client.send(
                    Message(text=text, mention=multi_mention, parse_mode="HTML"),
                    thread_id=thread_id,
                    thread_type=ThreadType.GROUP
                )
            except Exception as e:
                print(f"Lỗi khi gửi tin nhắn: {e}")

        except Exception as e:
            print(f"Lỗi: {e}")

    except ZaloAPIException as e:
        print(f"Lỗi API: {e}")
    except Exception as e:
        print(f"Lỗi chung: {e}")


def ft_vxkiue():
    return {
        'tagall': handle_tagall_command
    }
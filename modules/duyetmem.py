from zlapi.models import Message, MessageStyle, MultiMsgStyle
from config import ADMIN
import time

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Duyệt tất cả thành viên",
    'power': "Quản trị viên Bot / Quản trị viên Nhóm"
}

def handle_duyetmem_command(message, message_object, thread_id, thread_type, author_id, client):
    try:
        group_info = client.fetchGroupInfo(thread_id).gridInfoMap[thread_id]
        creator_id = group_info.get('creatorId')
        admin_ids = group_info.get('adminIds', [])

        if admin_ids is None:
            admin_ids = []

        all_admin_ids = set(admin_ids)
        all_admin_ids.add(creator_id)
        all_admin_ids.update(ADMIN)

        if author_id not in all_admin_ids and author_id not in ADMIN:
            client.replyMessage(
                Message(
                    text="🚫 Sếp ơi, có thèn đòi dùng lệnh sếp :33",
                ),
                message_object, thread_id, thread_type, ttl=12000
            )
            client.sendReaction(message_object, "❌", thread_id, thread_type, reactionType=75)
            return

        pending_members = group_info.pendingApprove.get('uids', [])

        command_parts = message.strip().split()

        if len(command_parts) < 2:
            client.replyMessage(
                Message(
                    text="Nhập như vầy nè Sếp :D\nduyetmem [all|list] not @user `✅`",
                ),
                message_object, thread_id, thread_type, ttl=12000
            )
            client.sendReaction(message_object, "❓Anh Quý đẹp trai", thread_id, thread_type, reactionType=75)
            return

        action = command_parts[1]

        if action == "list":
            if not pending_members:
                client.replyMessage(
                    Message(
                        text="Thưa Sếp, hiện tại không có thành viên nào đang chờ duyệt. 🚫",
                    ),
                    message_object, thread_id, thread_type, ttl=12000
                )
                client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
            else:
                client.replyMessage(
                    Message(
                        text=f"Thưa Sếp, số thành viên đang chờ duyệt: {len(pending_members)} thành viên 🗝️",
                    ),
                    message_object, thread_id, thread_type, ttl=12000
                )
                client.sendReaction(message_object, "🔍", thread_id, thread_type, reactionType=75)
        elif action == "all":
            if not pending_members:
                client.replyMessage(
                    Message(
                        text="Thưa Sếp, hiện tại không có thành viên nào đang chờ duyệt. 🚫",
                    ),
                    message_object, thread_id, thread_type, ttl=12000
                )
                client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)
                return

            for member_id in pending_members:
                if hasattr(client, 'handleGroupPending'):
                    client.handleGroupPending(member_id, thread_id)
                else:
                    break
                    
            client.replyMessage(
                Message(
                    text="Thưa Sếp, đã hoàn tất duyệt tất cả thành viên. ✅",
                ),
                message_object, thread_id, thread_type, ttl=12000
            )
            client.sendReaction(message_object, "✅ Anh Quý đẹp trai", thread_id, thread_type, reactionType=75)
        else:
            client.replyMessage(
                Message(
                    text="Nhập như vầy nè Sếp :D\nduyetmem [all|list] not @user `✅`",
                ),
                message_object, thread_id, thread_type, ttl=12000
            )
            client.sendReaction(message_object, "🚫", thread_id, thread_type, reactionType=75)

    except Exception as e:
        print(f"Lỗi: {e}")
        client.replyMessage(
            Message(
                text=f"Đã xảy ra lỗi khi duyệt.\n{e}",
            ),
            message_object, thread_id, thread_type, ttl=12000
        )
        client.sendReaction(message_object, "⚠️", thread_id, thread_type, reactionType=75)

def ft_vxkiue():
    return {
        'duyetmem': handle_duyetmem_command
    }
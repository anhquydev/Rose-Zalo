from zlapi.models import Message
from logging_utils import Logging

logger = Logging()

class LockBotHandler:
    def __init__(self, client):
        self.client = client

    def handle_lockbot_command(self, message_text, message_object, thread_id, thread_type, author_id):
        if author_id != self.client.ADMIN:
            self.client.replyMessage(Message(text="Chỉ admin mới có thể sử dụng lệnh này"), message_object, thread_id, thread_type)
            return
        
        user_ids_to_lock = []

        if message_object.mentions:
           user_ids_to_lock.extend([mention['uid'] for mention in message_object.mentions])
        else:
            try:
                potential_user_id = message_text.split()[-1]
                if potential_user_id.isdigit():
                    user_ids_to_lock.append(potential_user_id)
            except:
                self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..lockbot @người dùng hoặc ..lockbot <user_id>"), message_object, thread_id, thread_type)
                return
    
        if not user_ids_to_lock:
             self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..lockbot @người dùng hoặc ..lockbot <user_id>"), message_object, thread_id, thread_type)
             return

        for user_id_to_lock in user_ids_to_lock:
            try:
                user_info = self.client.fetchUserInfo(user_id_to_lock).changed_profiles.get(user_id_to_lock, {})
                user_name = user_info.get('zaloName', 'đéo xác định')
            except (IndexError, KeyError):
                 self.client.replyMessage(Message(text=f"Không tìm thấy thèn chóa {user_id_to_lock}."), message_object, thread_id, thread_type)
                 continue
            
            if user_id_to_lock == self.client.ADMIN:
                self.client.replyMessage(Message(text="Thèn chóa, mày định lock Admin tao à."), message_object, thread_id, thread_type)
                continue
            
            if user_id_to_lock not in self.client.locked_users:
                self.client.locked_users.append(user_id_to_lock)
                self.client.save_locked_users()
                self.client.replyMessage(Message(text=f"Đã lock thèn chóa {user_name} - {user_id_to_lock}"), message_object, thread_id, thread_type, ttl=10000)
                logger.warning(f"Đã lock thèn chóa {user_name} - {user_id_to_lock}")
            else:
                self.client.replyMessage(Message(text=f"Thèn chóa {user_name} - {user_id_to_lock} bị lock rồi mà."), message_object, thread_id, thread_type, ttl=10000)
    
    def handle_unlockbot_command(self, message_text, message_object, thread_id, thread_type, author_id):
        if author_id != self.client.ADMIN:
            self.client.replyMessage(Message(text="Chỉ admin mới có thể sử dụng lệnh này"), message_object, thread_id, thread_type)
            return
        
        user_ids_to_unlock = []

        if message_object.mentions:
           user_ids_to_unlock.extend([mention['uid'] for mention in message_object.mentions])
        else:
            try:
                potential_user_id = message_text.split()[-1]
                if potential_user_id.isdigit():
                    user_ids_to_unlock.append(potential_user_id)
            except:
                self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..unlockbot @người dùng hoặc ..unlockbot <user_id>"), message_object, thread_id, thread_type)
                return
        
        if not user_ids_to_unlock:
            self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..unlockbot @người dùng hoặc ..unlockbot <user_id>"), message_object, thread_id, thread_type)
            return
        
        for user_id_to_unlock in user_ids_to_unlock:
            try:
                user_info = self.client.fetchUserInfo(user_id_to_unlock).changed_profiles.get(user_id_to_unlock, {})
                user_name = user_info.get('zaloName', 'đéo xác định')
            except (IndexError, KeyError):
                 self.client.replyMessage(Message(text=f"Không tìm thấy thèn chóa {user_id_to_unlock}."), message_object, thread_id, thread_type)
                 continue

            if user_id_to_unlock in self.client.locked_users:
                self.client.locked_users.remove(user_id_to_unlock)
                self.client.save_locked_users()
                self.client.replyMessage(Message(text=f"Đã unlock thèn chóa {user_name} - {user_id_to_unlock}"), message_object, thread_id, thread_type, ttl=10000)
                logger.warning(f"Đã unlock thèn chóa {user_name} - {user_id_to_unlock}")
            else:
                self.client.replyMessage(Message(text=f"Thèn chóa {user_name} - {user_id_to_unlock} đã bị lock đâu Đại Ka."), message_object, thread_id, thread_type, ttl=10000)

    def handle_listlockbot_command(self, message_text, message_object, thread_id, thread_type, author_id):
        if author_id != self.client.ADMIN:
            self.client.replyMessage(Message(text="Chỉ admin mới có thể sử dụng lệnh này"), message_object, thread_id, thread_type)
            return
        if not self.client.locked_users:
            self.client.replyMessage(Message(text="Chưa có thèn chóa nào bị lock cả."), message_object, thread_id, thread_type)
            return
        
        locked_users_info = []
        for user_id in self.client.locked_users:
             user_info = self.client.fetchUserInfo(user_id).changed_profiles.get(user_id, {})
             user_name = user_info.get('zaloName', 'đéo xác định')
             locked_users_info.append(f"{user_name} - {user_id}")
        
        list_message = "\n".join(locked_users_info)    
        self.client.replyMessage(Message(text=f"Danh sách thèn chóa bị lockbot:\n\n{list_message}"), message_object, thread_id, thread_type)
from zlapi.models import Message
from logging_utils import Logging
logger = Logging()
class AntiSpamHandler:
    def __init__(self, client):
        self.client = client
    def handle_antispam_command(self, message, message_object, thread_id, thread_type, author_id):
            command = message.lower().split()
            if len(command) != 2:
                self.client.replyMessage(Message(text="Sử dụng: ..antispam on/off"), message_object, thread_id, thread_type, ttl=12000)
                return
            if str(author_id) not in self.client.ADMIN:
                self.client.replyMessage(Message(text="Bạn không có quyền sử dụng lệnh này."), message_object, thread_id, thread_type, ttl=5000)
                return
            action = command[1]
            if action == 'on':
                self.client.spam_enabled[thread_id] = True
                self.client.replyMessage(Message(text="Anti-spam đã được bật!"), message_object, thread_id, thread_type, ttl=5000)
            elif action == 'off':
                self.client.spam_enabled[thread_id] = False
                self.client.replyMessage(Message(text="Anti-spam đã được tắt!"), message_object, thread_id, thread_type, ttl=5000)
            else:
                self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..antispam on/off"), message_object, thread_id, thread_type, ttl=5000)
            self.client.save_spam_settings()
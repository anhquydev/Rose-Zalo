from zlapi.models import Message
from logging_utils import Logging

logger = Logging()

class AntiLinkHandler:
    def __init__(self, client):
        self.client = client

    def handle_antilink_command(self, message, message_object, thread_id, thread_type, author_id):
        command = message.lower().split()
        if len(command) < 2:
            self.client.replyMessage(Message(text="Sử dụng: `antilink on/off`"), message_object, thread_id, thread_type, ttl=5000)
            return

        if str(author_id) not in self.client.ADMIN:
            self.client.replyMessage(Message(text="Quyền Lồn Biên Giới 🛡️"), message_object, thread_id, thread_type, ttl=5000)
            return

        action = command[1]
        if action == 'on':
            self.client.antilink_enabled[thread_id] = True
            self.client.replyMessage(Message(text="Chống link đã được bật!"), message_object, thread_id, thread_type, ttl=5000)
        elif action == 'off':
            self.client.antilink_enabled[thread_id] = False
            self.client.replyMessage(Message(text="Chống link đã được tắt!"), message_object, thread_id, thread_type, ttl=5000)
        else:
            self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: `antilink on/off`"), message_object, thread_id, thread_type, ttl=5000)

        self.client.save_antilink_settings()
from zlapi.models import Message
from logging_utils import Logging
logger = Logging()
class LocTKHandler:
    def __init__(self, client):
        self.client = client
    def handle_loctk_command(self, message, message_object, thread_id, thread_type, author_id):
          command = message.lower().split()
          if len(command) < 2:
              self.client.replyMessage(Message(text="Sử dụng: `loctk on/off/add/remove/list`"), message_object, thread_id, thread_type, ttl=5000)
              return
          if str(author_id) not in self.client.ADMIN:
              self.client.replyMessage(Message(text="Bạn không có quyền sử dụng lệnh này."), message_object, thread_id, thread_type, ttl=5000)
              return
          action = command[1]
          if action == 'on':
              self.client.loctk_enabled[thread_id] = True
              self.client.replyMessage(Message(text="Lọc từ cấm đã được bật!"), message_object, thread_id, thread_type, ttl=5000)
          elif action == 'off':
             self.client.loctk_enabled[thread_id] = False
             self.client.replyMessage(Message(text="Lọc từ cấm đã được tắt!"), message_object, thread_id, thread_type, ttl=5000)
          elif action == 'add':
              if len(command) < 3:
                 self.client.replyMessage(Message(text="Sử dụng: ..loctk add <từ cần thêm>`"), message_object, thread_id, thread_type, ttl=12000)
                 return
              word_to_add = " ".join(command[2:])
              self.client.banned_words.append(word_to_add)
              self.client.save_banned_words()
              self.client.replyMessage(Message(text=f"Đã thêm từ cấm: {word_to_add}"), message_object, thread_id, thread_type, ttl=12000)
          elif action == 'remove':
              if len(command) < 3:
                  self.client.replyMessage(Message(text="Sử dụng: ..loctk remove <từ cần xóa>`"), message_object, thread_id, thread_type, ttl=12000)
                  return
              word_to_remove = " ".join(command[2:])
              if word_to_remove in self.client.banned_words:
                  self.client.banned_words.remove(word_to_remove)
                  self.client.save_banned_words()
                  self.client.replyMessage(Message(text=f"Đã xóa từ cấm: {word_to_remove}"), message_object, thread_id, thread_type, ttl=12000)
              else:
                  self.client.replyMessage(Message(text="Không tìm thấy từ cấm trong danh sách."), message_object, thread_id, thread_type, ttl=12000)
          elif action == 'list':
              if not self.client.banned_words:
                  self.client.replyMessage(Message(text="Danh sách từ cấm hiện tại trống."), message_object, thread_id, thread_type, ttl=12000)
              else:
                banned_words_list = "\n".join(f"{word}" for word in self.client.banned_words)
                self.client.replyMessage(Message(text=f"Danh sách từ cấm:\n{banned_words_list}"), message_object, thread_id, thread_type, ttl=24000)
          else:
              self.client.replyMessage(Message(text="Commands Not Found. Sử dụng: ..loctk on/off/add/remove/list"), message_object, thread_id, thread_type, ttl=5000)
          self.client.save_loctk_settings()
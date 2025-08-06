import json, os, time, sys, random, re, unicodedata
from datetime import datetime, timedelta
from queue import Queue
import threading
import logging
import urllib.parse
import queue
import math
from PIL import Image
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import ffmpeg
import pyfiglet
from colorama import Fore, Style, init
from zlapi import ZaloAPI
from zlapi.models import *
from config import API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES, ADMIN, PREFIX
from xkprj import CommandHandler
from logging_utils import Logging
from event.event import handleGroupEvent
from threading import Lock
from commands.antispam import AntiSpamHandler
from commands.antilink import AntiLinkHandler
from commands.loctk import LocTKHandler
from commands.antiundo import UndoHandler
from commands.lockbot import LockBotHandler
from commands.tiktok import TiktokHandler
init(autoreset=True)
COLORS = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.WHITE]
def banner():
    text = """
• Bot By Anh Quý •
"""
    for i, char in enumerate(text):
        color = COLORS[i % len(COLORS)]
        print(color + char, end='')
banner()

class ResetBot:
    def __init__(self, reset_interval=900):
        self.reset_event = threading.Event()
        self.reset_interval = reset_interval
        self.load_autorestart_setting()

    def load_autorestart_setting(self):
        try:
            with open("seting.json", "r") as f:
                settings = json.load(f)
                self.autorestart = settings.get("autorestart", "False") == "True"
            
            if self.autorestart:
                logger.restart("Chế độ auto restart đang được bật")
                threading.Thread(target=self.reset_code_periodically, daemon=True).start()
            else:
                logger.restart("Chế độ auto restart đang được tắt")
        except Exception as e:
            logger.error(f"Lỗi khi tải cấu hình autorestart: {e}")
            self.autorestart = False

    def reset_code_periodically(self):
        while not self.reset_event.is_set():
            time.sleep(self.reset_interval)
            logger.restart("Đang tiến hành khởi động lại bot...")
            self.restart_bot()

    def restart_bot(self):
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            gui_message = f"Bot khởi động lại thành công vào lúc: {current_time}"
            logger.restart(gui_message)
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            logger.error(f"Lỗi khi khởi động lại bot: {e}")

logger = Logging()

class Client(ZaloAPI):
    def __init__(self, api_key, secret_key, imei, session_cookies, reset_interval=3600, auto_approve_interval=0):
        super().__init__(api_key, secret_key, imei=imei, session_cookies=session_cookies)
        self.command_handler = CommandHandler(self)
        self.reset_bot = ResetBot(reset_interval)
        self.session = requests.Session()
        retry_strategy = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.message_queue = Queue()
        self.processed_messages = set()
        self.response_time_limit = timedelta(seconds=1)
        self.ADMIN = ADMIN
        self.group_info_cache = {}
        self.last_sms_times = {}
        self.temp_thread_storage = {}
        self.search_results = {}
        self.search_result_messages = {}
        self.search_result_ttl = 24
        self.spam_enabled = self.load_spam_settings()
        self.user_message_times = {}
        self.warned_users = {}
        self.spam_threshold = 5
        self.kick_threshold = 6
        self.spam_window = 7
        self.loctk_enabled = self.load_loctk_settings()
        self.banned_words = self.load_banned_words()
        self.banned_word_violations = {}
        self.FileNM = 'database/dataundo.json'
        self.undo_enabled = self.load_undo_settings()
        self.locked_users_file = 'data/locked_users.json'
        self.locked_users = self.load_locked_users()
        self.last_undo_reset = self.load_last_undo_reset()
        self.antilink_enabled = self.load_antilink_settings()
        self.check_and_reset_undo()
        self.antispam_handler = AntiSpamHandler(self)
        self.loctk_handler = LocTKHandler(self)
        self.undo_handler = UndoHandler(self)
        self.lockbot_handler = LockBotHandler(self)
        self.tiktok_handler = TiktokHandler(self)
        self.antilink_handler = AntiLinkHandler(self)
        self.auto_approve_enabled = self.load_auto_approve_settings()
        self.auto_approve_interval = auto_approve_interval
        self.last_auto_approve_check = datetime.min
        self.group_message_counts = {}
        self.settings = self.load_settings()
        self.duyetbox_data = self.load_duyetbox_data()
        self.ADMIN = self.settings.get("admin")
        self.ADM = self.settings.get("adm", [])
        self.sendtask_autosticker_file = "modules/cache/sendtask_autosticker.json"
        self.datasticker_file = "database/datasticker.json"
        threading.Thread(target=self.cleanup_expired_search_results, daemon=True).start()
        threading.Thread(target=self.auto_approve_periodically, daemon=True).start()
        logger.logger('EVENT GROUP', 'Tiến hành nhận sự kiện các nhóm...')
        self.load_sticker_data()
        
    def load_sticker_data(self):
        try:
            with open(self.datasticker_file, "r") as f:
                self.sticker_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.sticker_data = []
            self.save_sticker_data()

    def save_sticker_data(self):
        with open(self.datasticker_file, "w") as f:
            json.dump(self.sticker_data, f, indent=4)

    def load_allowed_groups(self):
        try:
            with open(self.sendtask_autosticker_file, "r") as f:
                return json.load(f).get("groups", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_allowed_groups(self, allowed_groups):
        with open(self.sendtask_autosticker_file, "w") as f:
            json.dump({"groups": allowed_groups}, f, indent=4)

    def auto_approve_periodically(self):
        while True:
            self.check_and_handle_auto_approve()
            time.sleep(self.auto_approve_interval)

    def onEvent(self,event_data,event_type):
	    handleGroupEvent(self,event_data,event_type)

    def send_request(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi request: {e}")
            return None

    def load_auto_approve_settings(self):
        try:
            with open("data/auto_approve_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logger.error("Lỗi khi đọc file auto_approve_settings.json. Khởi tạo settings trống.")
            return {}

    def save_auto_approve_settings(self):
        try:
            with open("data/auto_approve_settings.json", "w") as f:
                json.dump(self.auto_approve_enabled, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt auto-approve: {e}")

    def handle_auto_approve_command(self, message_text, message_object, thread_id, thread_type, author_id):
        if author_id not in self.ADMIN:
            self.replyMessage(Message(text="Bạn không có quyền sử dụng lệnh này."), message_object, thread_id, thread_type)
            return

        parts = message_text.split()
        if len(parts) < 2:
            self.replyMessage(Message(text="Cách dùng: .autoapprv <on/off>"), message_object, thread_id, thread_type)
            return

        action = parts[1].lower()
        if action == "on":
            self.auto_approve_enabled[thread_id] = True
            self.save_auto_approve_settings()
            self.replyMessage(Message(text="Đã bật tự động duyệt thành viên mới."), message_object, thread_id, thread_type)
        elif action == "off":
            self.auto_approve_enabled[thread_id] = False
            self.save_auto_approve_settings()
            self.replyMessage(Message(text="Đã tắt tự động duyệt thành viên mới."), message_object, thread_id, thread_type)
        else:
            self.replyMessage(Message(text="Lệnh không hợp lệ. Sử dụng 'on' hoặc 'off'."), message_object, thread_id, thread_type)

    def load_spam_settings(self):
        try:
            with open("data/spam_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logger.error("Lỗi khi đọc file spam_settings.json. Khởi tạo settings trống.")
            return {}

    def save_spam_settings(self):
        try:
            with open("data/spam_settings.json", "w") as f:
                json.dump(self.spam_enabled, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt anti-spam: {e}")

    def load_loctk_settings(self):
        try:
            with open("data/loctk_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            logger.error("Lỗi khi đọc file loctk_settings.json. Khởi tạo settings trống.")
            return {}

    def save_loctk_settings(self):
         try:
            with open("data/loctk_settings.json", "w") as f:
                json.dump(self.loctk_enabled, f, indent=4)
         except Exception as e:
             logger.error(f"Lỗi khi lưu cài đặt lọc từ: {e}")

    def load_banned_words(self):
        try:
            with open("data/banned_words.json", "r", encoding='utf-8') as f:
                data = json.load(f)
                return data.get("banned_words", {"words": []}).get("words", [])
        except FileNotFoundError:
            logger.error("File banned_words.json không tìm thấy.")
            return []
        except json.JSONDecodeError:
            logger.error("Lỗi khi đọc file banned_words.json. ")
            return []

    def save_banned_words(self):
        try:
             with open("data/banned_words.json", "w", encoding='utf-8') as f:
                json.dump({"banned_words": {"words": self.banned_words}}, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Lỗi khi lưu danh sách từ cấm: {e}")

    def load_undo_settings(self):
        try:
            with open("data/undo_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"groups": {}}
        except json.JSONDecodeError:
            logger.error("Lỗi khi đọc file undo_settings.json. Khởi tạo settings mặc định.")
            return {"groups": {}}

    def save_undo_settings(self):
        try:
            with open("data/undo_settings.json", "w") as f:
                json.dump(self.undo_enabled, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt undo: {e}")

    def Luuvideo(self, cliMsgId):
        with open(self.FileNM, 'r') as f:
            messages = json.load(f)
        cliMsgId = str(cliMsgId)
        for message in messages:
            if message['cliMsgId'] == cliMsgId:
                return message['content']
        return None

    def FileUndo(self):
        try:
            if not os.path.exists(self.FileNM):
                with open(self.FileNM, 'w') as f:
                    json.dump([], f)
            else:
                with open(self.FileNM, 'r') as f:
                    json.load(f)
        except (json.JSONDecodeError, OSError, IOError):
            with open(self.FileNM, 'w') as f:
                json.dump([], f)

    def message_object_undo(self, message_object, message_text):
        content = message_object.content if isinstance(message_object.content, dict) else {}
        if isinstance(content, dict) and 'href' in content:
            stored_content = {
                'href': content.get('href'),
                'thumb': content.get('thumb'),
                'params': content.get('params', {})
            }
        else:
           stored_content = content
        return {
            'msgId': message_object.msgId,
            'uidFrom': message_object.uidFrom,
            'cliMsgId': message_object.cliMsgId,
            'msgType': message_object.msgType,
            'content': stored_content,
            'text': message_text,
            'params': message_object.params,
            'id': content.get('id', ''),
            'catId': content.get('catId', '')
        }

    def LuuNoiDungThuHoi(self, message_object, message_text):
        noidung_1 = self.message_object_undo(message_object, message_text)
        with open(self.FileNM, 'r') as f:
            messages = json.load(f)
        messages.append(noidung_1)
        with open(self.FileNM, 'w') as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)

    def load_last_undo_reset(self):
        try:
            with open("data/undo_reset.json", "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_reset',datetime.min.isoformat()))
        except (FileNotFoundError, json.JSONDecodeError):
            return datetime.min

    def save_last_undo_reset(self, last_reset_time):
        try:
            with open("data/undo_reset.json", "w") as f:
                json.dump({"last_reset": last_reset_time.isoformat()}, f, indent=4)
        except Exception as e:
           logger.error(f"Lỗi khi lưu thời gian reset undo: {e}")

    def check_and_reset_undo(self):
        now = datetime.now()
        if (now - self.last_undo_reset) >= timedelta(days=1):
            self.reset_undo_data()
            self.last_undo_reset = now
            self.save_last_undo_reset(now)
    def reset_undo_data(self):
        try:
             with open(self.FileNM, 'w') as f:
                json.dump([], f)
             logger.info("Đã xóa nội dung file undo.json.")
        except Exception as e:
             logger.error(f"Lỗi khi xóa nội dung file undo.json: {e}")
    def TimTinNhanThuHoi(self, cliMsgId):
        with open(self.FileNM, 'r') as f:
            messages = json.load(f)
        cliMsgId = str(cliMsgId)
        for message in messages:
            if message['cliMsgId'] == cliMsgId:
                return message['id'], message['catId']
        return None, None

    def Anhthuhoi(self, cliMsgId):
        with open(self.FileNM, 'r') as f:
            messages = json.load(f)
        cliMsgId = str(cliMsgId)
        for message in messages:
            if message['cliMsgId'] == cliMsgId:
                return message['content']
        return None

    def DownAnhThuHoi(self, media_url, anh='undo.jpg'):
        try:
            response = requests.get(media_url)
            response.raise_for_status()
            with open(anh, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
           logger.error(f"Lỗi khi tải ảnh thu hồi: {e}")
           return None
        return anh

    def send_sticker(self, id, catId, thread_id, thread_type, author_id, message_object):
        try:
            author_name = self.fetchUserInfo(author_id).name
            text = f"@{author_name} vừa thu hồi:"
            offset = text.find(f"@{author_name}")
            self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
            self.sendSticker(1, id, catId, thread_id, thread_type)
        except Exception as e:
            logger.error(f"Lỗi khi gửi sticker: {e}")

    def handle_lockbot_command(self, message_text, message_object, thread_id, thread_type, author_id):
         self.lockbot_handler.handle_lockbot_command(message_text, message_object, thread_id, thread_type, author_id)

    def handle_unlockbot_command(self, message_text, message_object, thread_id, thread_type, author_id):
        self.lockbot_handler.handle_unlockbot_command(message_text, message_object, thread_id, thread_type, author_id)

    def load_mute_list(self):
       mute_vxk = "data/khoamom.json"
       if os.path.exists(mute_vxk):
         with open(mute_vxk, 'r') as f:
            return json.load(f)
       return {}

    def is_user_muted(self, thread_id, author_id):
       mute_list = self.load_mute_list()
       if thread_id in mute_list:
         return str(author_id) in mute_list[thread_id]
       return False

    def load_antilink_settings(self):
        try:
            with open("data/antilink_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
             logger.error("Lỗi khi đọc file antilink_settings.json. Khởi tạo settings trống.")
             return {}

    def save_antilink_settings(self):
        try:
            with open("data/antilink_settings.json", "w") as f:
                 json.dump(self.antilink_enabled, f, indent=4)
        except Exception as e:
            logger.error(f"Lỗi khi lưu cài đặt antilink: {e}")

    def hex_to_ansi(hex_color):
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                raise ValueError("Mã màu không hợp lệ")
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f'\033[38;2;{r};{g};{b}m'
        except Exception as e:
            logger.error(f"Lỗi trong hex_to_ansi: {e}")
            return '\033[0m'  # reset màu mặc định        

    def is_group_admin(self, thread_id, user_id):
        try:
            if thread_id in self.group_info_cache:
                group_data = self.group_info_cache[thread_id]
            else:
                group_info = self.fetchGroupInfo(thread_id)
                if not group_info or not hasattr(group_info, 'gridInfoMap') or thread_id not in group_info.gridInfoMap:
                     logger.error(f"Không tìm thấy thông tin nhóm hoặc gridInfoMap cho thread_id: {thread_id}")
                     return False
                group_data = group_info.gridInfoMap[thread_id]
                self.group_info_cache[thread_id] = group_data
            creator_id = group_data.get('creatorId')
            admin_ids = group_data.get('adminIds', [])
            return user_id == creator_id or user_id in admin_ids
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra admin nhóm: {e}")
            return False

    def get_content_message(self, message_object):
        if message_object.msgType == 'chat.sticker':
            return ""

        content = message_object.content

        if isinstance(content, dict) and 'title' in content:
            text_to_check = content['title']
        else:
            text_to_check = content if isinstance(content, str) else ""
        return text_to_check

    def is_url_in_message(self, message_object):
        if message_object.msgType == 'chat.sticker':
            return False
        
        text_to_check = self.get_content_message(message_object)

        url_regex = re.compile(
            r'http[s]?://'
            r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        if re.search(url_regex, text_to_check):
            return True
        
        return False
    
    def get_allow_link_status(self, thread_id):
        return self.antilink_enabled.get(thread_id, False)

    def check_and_handle_auto_approve(self):
        now = datetime.now()
        if (now - self.last_auto_approve_check).total_seconds() >= self.auto_approve_interval:
            for thread_id, enabled in self.auto_approve_enabled.items():
                if enabled == True:
                    self.auto_approve_pending_members(thread_id)
            self.last_auto_approve_check = now

    def auto_approve_pending_members(self, thread_id):
        try:
            group_info = self.fetchGroupInfo(thread_id)
            if not group_info or not hasattr(group_info, 'gridInfoMap'):
                return False
            group_data = group_info.get('gridInfoMap', {}).get(thread_id)
            if not isinstance(group_data, dict):
              return False
            pending_members = group_data.get('pendingApprove', {}).get('uids', [])
            for member_id in pending_members:
                if hasattr(self, 'handleGroupPending'):
                    if thread_id in self.auto_approve_enabled:
                        self.handleGroupPending(member_id, thread_id)
            return True
        except Exception as e:
            return False

    def handle_auto_sticker(self, thread_id, thread_type, message_object):
        allowed_groups = self.load_allowed_groups()  
        if thread_type == ThreadType.GROUP and thread_id in allowed_groups:
            if message_object.msgType == "webchat":
                self.group_message_counts[thread_id] = self.group_message_counts.get(thread_id, 0) + 1
                if self.group_message_counts[thread_id] >= random.randint(10, 15):
                    if self.sticker_data:
                        sticker = random.choice(self.sticker_data)
                        self.sendSticker(1, sticker["id"], sticker["catId"], thread_id, thread_type)
                        self.group_message_counts[thread_id] = 0

    def load_settings(self):
        try:
            with open("seting.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Không tìm thấy file setting.json")
            return {}
        except json.JSONDecodeError:
            logger.error("Lỗi giải mã JSON trong file setting.json")
            return {}

    def load_duyetbox_data(self):
        try:
            with open("modules/cache/duyetboxdata.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Không tìm thấy file duyetboxdata.json")
            return []
        except json.JSONDecodeError:
            logger.error("Lỗi giải mã JSON trong file duyetboxdata.json")
            return []

    def is_allowed_author(self, author_id):
        return str(author_id) in self.ADM or str(author_id) == str(self.ADMIN)

    def is_duyetbox_thread(self, thread_id):
        return str(thread_id) in self.duyetbox_data

    def onMessage(self, mid, author_id, message, message_object, thread_id, thread_type):
        try:
            message_text = message.text if isinstance(message, Message) else str(message)
            author_name = self.fetchUserInfo(author_id).changed_profiles.get(author_id, {}).get('zaloName', 'đéo xác định')
            logger.info(f"{message}")

            if self.is_user_muted(thread_id, author_id):
                self.deleteGroupMsg(message_object.msgId, author_id, message_object.cliMsgId, thread_id)
                return

            if author_id in self.locked_users:
                return

            if self.get_allow_link_status(thread_id) and self.is_url_in_message(message_object) and author_id not in ADMIN:
                if not self.is_group_admin(thread_id, author_id):
                  self.deleteGroupMsg(message_object.msgId, author_id, message_object.cliMsgId, thread_id)
                  self.replyMessage(Message(text=f"⚠️ Cảnh cáo {author_name} không được gửi link vào nhóm \n Cẩn thận admin cho ăn mute nha thằng nguu"), message_object, author_id, ThreadType.USER)
                  return
            if message_object.msgType == 'chat.sticker':
                allowed_groups = self.load_allowed_groups()
                if thread_type == ThreadType.GROUP and thread_id in allowed_groups:
                    sticker_id = message_object.content.id
                    sticker_catId = message_object.content.catId
                    logger.info(f"Sticker ID: {sticker_id}, Sticker CatId: {sticker_catId}")
                    sticker_info = {"id": sticker_id, "catId": sticker_catId}
                    if sticker_info not in self.sticker_data:
                        self.sticker_data.append(sticker_info)
                        self.save_sticker_data()

            command_handlers = {
                ".tiktok": self.tiktok_handler.handle_tiktok_command,
                ".antispam": self.antispam_handler.handle_antispam_command,
                ".loctk": self.loctk_handler.handle_loctk_command,
                ".antiundo": self.undo_handler.handle_undo_command,
                ".lockbot": self.lockbot_handler.handle_lockbot_command,
                ".unlockbot": self.lockbot_handler.handle_unlockbot_command,
                ".listlb": self.lockbot_handler.handle_listlockbot_command,
                ".antilink": self.antilink_handler.handle_antilink_command,
                ".autoapprv": self.handle_auto_approve_command
            }

            for prefix, handler in command_handlers.items():
                if message_text.lower().startswith(prefix):
                    handler(message_text, message_object, thread_id, thread_type, author_id)
                    return

            if message_text.isdigit() and thread_id in self.search_results and author_id in self.search_results[thread_id]:
                self.handle_download_command(message_text, message_object, thread_id, thread_type, author_id)
                return

            self.command_handler.handle_command(message_text, author_id, message_object, thread_id, thread_type)
            self.handle_auto_sticker(thread_id, thread_type, message_object)

        except Exception as e:
            logger.error(f"Lỗi trong onMessage: {e}")
            if message and thread_type == ThreadType.USER:
                if author_id == self.uid:
                    return
                now = time.time()
                if author_id in self.temp_thread_storage:
                    last_message_time = self.temp_thread_storage[author_id]
                    if now - last_message_time < 360000:
                        return
                self.temp_thread_storage[author_id] = now
                msg = f'''
Tham Gia Group để nhận thông báo
https://zalo.me/g/utwkzk998
'''
                self.replyMessage(Message(text=msg), message_object, thread_id, thread_type, ttl=300000)
                self.sendBusinessCard(userId=790318026347075757, qrCodeUrl=self.fetchUserInfo(self.uid).changed_profiles[self.uid]['avatarUrl'], phone="VXK_ZaloBot!", thread_id=thread_id, thread_type=thread_type, ttl=300000)

        self.check_spam(author_id, message_object, thread_id, thread_type)
        if str(author_id) not in ADMIN:
            self.check_banned_words(message_text, message_object, thread_id, thread_type, author_id)

        if self.is_undo_enabled(thread_id):
            if message_object.msgType == 'chat.undo':
                pyc_1 = str(message_object.content['cliMsgId'])
                pyc_2 = self.Anhthuhoi(pyc_1)
                pyc_3 = self.Luuvideo(pyc_1)
                stored_message = next((msg for msg in self.load_message_history() if str(msg.get('cliMsgId')) == pyc_1), None)
                if pyc_3:
                    if 'href' in pyc_3 and pyc_3['href']:
                        try:
                            if 'params' in pyc_3 and '"video_original_width"' in pyc_3['params']:
                                video_thuhoi = pyc_3['href']
                                thumb_thuhoi = pyc_3['thumb']
                                params = pyc_3['params']
                                thuhoi_par = json.loads(params)
                                duration = thuhoi_par.get('duration', '')
                                width = thuhoi_par.get('video_width', '')
                                height = thuhoi_par.get('video_height', '')
                                original_title = ""
                                if stored_message and stored_message.get('text'):
                                    try:
                                        original_title = stored_message['text'].split("title='")[1].split("',")[0]
                                    except:
                                        original_title = ""

                                text_title = f"{original_title}"
                                author_name = self.fetchUserInfo(author_id).name
                                text = f"@{author_name} vừa thu hồi:"
                                offset = text.find(f"@{author_name}")
                                self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
                                self.sendRemoteVideo(
                                    videoUrl=video_thuhoi,
                                    thumbnailUrl=thumb_thuhoi,
                                    duration=duration,
                                    width=width,
                                    height=height,
                                    message=Message(text=text_title),
                                    thread_id=thread_id,
                                    thread_type=thread_type,
                                    ttl=720000
                                )
                        except Exception as e:
                            logger.error(f"Lỗi khi gửi video: {e}")
                if pyc_2:
                    if isinstance(pyc_2, dict) and 'href' in pyc_2:
                        if 'jpg' in pyc_2['href'] or 'png' in pyc_2['href']:
                            anh_path = self.DownAnhThuHoi(pyc_2['thumb'])
                            if anh_path:
                                href = pyc_2['href']
                                image = Image.open(anh_path)
                                width, height = image.size
                                original_title = ""
                                if stored_message and stored_message.get('text'):
                                    try:
                                        original_title = stored_message['text'].split("title='")[1].split("',")[0]
                                    except:
                                        original_title = ""

                                author_name = self.fetchUserInfo(author_id).name
                                text = f"@{author_name} vừa thu hồi:"
                                offset = text.find(f"@{author_name}")
                                self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
                                self.sendLocalImage(anh_path,
                                    width=width,
                                    height=height,
                                    message=Message(text=f"{original_title}", ),
                                    thread_id=thread_id,
                                    thread_type=thread_type,
                                    ttl=720000
                                )
                                os.remove(anh_path)
                elif stored_message and stored_message.get('text'):
                    author_name = self.fetchUserInfo(author_id).name
                    text = f"@{author_name} vừa thu hồi: {stored_message.get('text')}"
                    offset = text.find(f"@{author_name}")
                    self.replyMessage(
                        Message(text=text, mention=Mention(author_id, length=len(f"@{author_name}"), offset=offset)),
                        message_object,
                        thread_id,
                        thread_type,
                        ttl=720000
                    )

            if message_object.msgType == 'chat.undo':
                pyc_1 = str(message_object.content['cliMsgId'])
                pyc_id, pyc_catId = self.TimTinNhanThuHoi(pyc_1)
                if pyc_id and pyc_catId:
                    self.send_sticker(pyc_id, pyc_catId, thread_id, thread_type, author_id, message_object)
            else:
                self.LuuNoiDungThuHoi(message_object, message_text)

            if message_object.msgType == 'chat.undo':
                pyc_1 = str(message_object.content['cliMsgId'])
                pyc_4 = self.Luuvideo(pyc_1)
                if pyc_4:
                    if 'href' in pyc_4 and pyc_4['href'] and 'aac' in pyc_4['href']:
                        try:
                            voice_url = pyc_4['href']
                            author_name = self.fetchUserInfo(author_id).name
                            text = f"@{author_name} vừa thu hồi:"
                            offset = text.find(f"@{author_name}")
                            self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
                            self.sendRemoteVoice(voice_url, thread_id, thread_type, fileSize=1)
                        except Exception as e:
                            logger.error(f"Lỗi khi gửi voice thu hồi: {e}")

            if message_object.msgType == 'chat.undo':
                pyc_1 = str(message_object.content['cliMsgId'])
                original_message = next((msg for msg in self.load_message_history() if str(msg.get('cliMsgId')) == pyc_1), None)
                if original_message and original_message.get('msgType') == 'share.file':
                    try:
                        file_url = original_message['content']['href']
                        file_name = original_message['text'].split("title='")[1].split("',")[0]
                        file_extension = original_message['content']['params'].split("fileExt\":\"")[1].split("\"")[0]
                        author_name = self.fetchUserInfo(author_id).name
                        text = f"@{author_name} vừa thu hồi:"
                        offset = text.find(f"@{author_name}")
                        self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
                        self.sendRemoteFile(
                            fileUrl=file_url,
                            fileName=file_name,
                            thread_id=thread_id,
                            thread_type=thread_type,
                            fileSize=None,
                            extension=file_extension
                        )

                    except Exception as e:
                        logger.error(f"Lỗi khi gửi lại file thu hồi: {e}")

        if self.is_undo_enabled(thread_id) and message_object.msgType == 'chat.undo':
            pyc_1 = str(message_object.content['cliMsgId'])
            original_message = next((msg for msg in self.load_message_history() if str(msg.get('cliMsgId')) == pyc_1), None)
            if original_message and original_message.get('msgType') == 'chat.recommended':
                try:
                    user_id = original_message['content']['params']
                    phone = original_message['text'].split("phone\":\"")[1].split("\",")[0]
                    author_name = self.fetchUserInfo(author_id).name
                    text = f"@{author_name} vừa thu hồi:"
                    offset = text.find(f"@{author_name}")
                    self.replyMessage(Message(text=text, mention=Mention(author_id, len(f"@{author_name}"), offset)), message_object, thread_id, thread_type, ttl=720000)
                    self.sendBusinessCard(
                        userId=user_id,
                        qrCodeUrl=None,
                        thread_id=thread_id,
                        thread_type=thread_type,
                        phone=phone
                    )

                except Exception as e:
                    logger.error(f"Lỗi khi gửi lại Business Card thu hồi: {e}")
    def is_undo_enabled(self, thread_id):
        if thread_id in self.undo_enabled.get("groups", {}):
            return self.undo_enabled["groups"][thread_id]
        return False
    def load_locked_users(self):
        try:
            with open(self.locked_users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    def save_locked_users(self):
        with open(self.locked_users_file, 'w') as f:
            json.dump(self.locked_users, f, indent=4)
    def load_message_history(self):
        try:
           with open(self.FileNM, 'r') as f:
            return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
             logger.error(f"Lỗi đọc lịch sử tin nhắn: {e}")
             return []
    def handle_undo_command(self, message, message_object, thread_id, thread_type, author_id):
        self.undo_handler.handle_undo_command(message, message_object, thread_id, thread_type, author_id)

    def check_banned_words(self, message, message_object, thread_id, thread_type, author_id):
        if not self.loctk_enabled.get(thread_id, False):
              return
        if self.is_admin(author_id, thread_id):
            return
        normalized_message = unicodedata.normalize('NFKC', message).lower()
        for word in self.banned_words:
            normalized_word = unicodedata.normalize('NFKC', word).lower()
            if re.search(r'\b' + re.escape(normalized_word) + r'\b', normalized_message):
                self.deleteGroupMsg(message_object.msgId, author_id, message_object.cliMsgId, thread_id)
                self.record_banned_word_violation(author_id, thread_id, message_object)
                return
    def record_banned_word_violation(self, user_id, thread_id, message_object):
        if thread_id not in self.banned_word_violations:
            self.banned_word_violations[thread_id] = {}
        if user_id not in self.banned_word_violations[thread_id]:
            self.banned_word_violations[thread_id][user_id] = 0
        self.banned_word_violations[thread_id][user_id] += 1
        violations = self.banned_word_violations[thread_id][user_id]
        user_info = self.fetchUserInfo(user_id)
        if user_info and user_id in user_info.changed_profiles:
          user_name = user_info.changed_profiles[user_id].zaloName
        else:
            user_name = "Người dùng"
        if violations == 3:
          self.replyMessage(Message(text=f"Sắp cút rồi đấy."), message_object, thread_id, ThreadType.GROUP, ttl=12000)
        elif violations >= 5:
          self.blockUsersInGroup(user_id, thread_id)
    def should_kick_user(self, user_id, thread_id):
        if thread_id in self.banned_word_violations and user_id in self.banned_word_violations[thread_id]:
          return self.banned_word_violations[thread_id][user_id] >= 5
        return False
    def handle_loctk_command(self, message, message_object, thread_id, thread_type, author_id):
          if self.loctk_handler:
            self.loctk_handler.handle_loctk_command(message, message_object, thread_id, thread_type, author_id)
          
    def handle_antispam_command(self, message, message_object, thread_id, thread_type, author_id):
        if self.antispam_handler:
             self.antispam_handler.handle_antispam_command(message, message_object, thread_id, thread_type, author_id)

    def is_admin(self, user_id, thread_id):
        group_data = self.fetchGroupInfo(thread_id)
        if not group_data or thread_id not in group_data.gridInfoMap:
            return False
        group_data = group_data.gridInfoMap[thread_id]
        admins = group_data.get('adminIds', [])
        owners = group_data.get('creatorId')
        return user_id in admins or user_id == owners

    def check_spam(self, author_id, message_object, thread_id, thread_type):
        if not self.spam_enabled.get(thread_id, False):
            return
        if self.is_admin(author_id, thread_id):
            return

        now = time.time()
        if thread_id not in self.user_message_times:
            self.user_message_times[thread_id] = {}
        if author_id not in self.user_message_times[thread_id]:
            self.user_message_times[thread_id][author_id] = []
        user_messages = self.user_message_times[thread_id][author_id]
        user_messages.append(now)
        user_messages = [timestamp for timestamp in user_messages if now - timestamp <= self.spam_window]
        self.user_message_times[thread_id][author_id] = user_messages
        if len(user_messages) == self.spam_threshold:
            self.handle_spam_warn(author_id, message_object, thread_id, thread_type)
        elif len(user_messages) >= self.kick_threshold:
            self.handle_spam_violation(author_id, message_object, thread_id, thread_type)
            del self.user_message_times[thread_id][author_id]

    def handle_spam_warn(self, user_id, message_object, thread_id, thread_type):
        user_info = self.fetchUserInfo(user_id)
        if not user_info or user_id not in user_info.changed_profiles:
            return
        user_name = user_info.changed_profiles[user_id].zaloName
        msg = f"@{user_name} chậm thôi em zai"
        offset = msg.find(f"@{user_name}")
        self.replyMessage(Message(text=msg, mention=Mention(user_id, length=len("@{user_name}"), offset=offset)), message_object, thread_id, thread_type, ttl=30000)
        if user_id not in self.warned_users:
            self.warned_users[user_id] = {}
        self.warned_users[user_id][thread_id] = True

    def handle_spam_violation(self, user_id, message_object, thread_id, thread_type):
        user_info = self.fetchUserInfo(user_id)
        if not user_info or user_id not in user_info.changed_profiles:
          return
        user_name = user_info.changed_profiles[user_id].zaloName
        
        if self.is_admin(user_id, thread_id):
           return

        group_info = self.fetchGroupInfo(thread_id)
        if not group_info or thread_id not in group_info.gridInfoMap:
            self.send_error_message(thread_id, thread_type, "Không thể lấy thông tin nhóm.")
            return
        group_data = group_info.gridInfoMap[thread_id]
        creator_id = group_data.get('creatorId')
        admin_ids = group_data.get('adminIds', [])
        if self.uid not in admin_ids and self.uid != creator_id:
          return

        if user_id in admin_ids or user_id == creator_id:
            return

        self.blockUsersInGroup(user_id, thread_id)
        if user_id in self.warned_users and thread_id in self.warned_users[user_id]:
            del self.warned_users[user_id][thread_id]

    def handle_tiktok_command(self, message, message_object, thread_id, thread_type, author_id):
         self.tiktok_handler.handle_tiktok_command(message, message_object, thread_id, thread_type, author_id)
    def get_video_info(self, video_url):
        try:
            probe = ffmpeg.probe(video_url)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream:
                duration = float(video_stream['duration']) * 1000
                width = int(video_stream['width'])
                height = int(video_stream['height'])
                return duration, width, height
            else:
                raise Exception("Không tìm thấy luồng video trong URL")
        except Exception as e:
            raise Exception(f"Lỗi khi lấy thông tin video: {str(e)}")

    def cleanup_search_result(self, thread_id, author_id):
        if thread_id in self.search_results and author_id in self.search_results[thread_id]:
          del self.search_results[thread_id][author_id]
          if not self.search_results[thread_id]:
              del self.search_results[thread_id]
        if thread_id in self.search_result_messages and author_id in self.search_result_messages[thread_id]:
          del self.search_result_messages[thread_id][author_id]
          if not self.search_result_messages[thread_id]:
            del self.search_result_messages[thread_id]

    def handle_download_command(self, message, message_object, thread_id, thread_type, author_id):
        try:
            if thread_id not in self.search_results or author_id not in self.search_results[thread_id]:
                return False
            if thread_id in self.search_result_messages and author_id in self.search_result_messages[thread_id]:
                search_result_info = self.search_result_messages[thread_id][author_id]
                elapsed_time = self.get_current_time() - search_result_info['time']
                if elapsed_time > self.search_result_ttl:
                    self.cleanup_search_result(thread_id, author_id)
                    return False
            match = re.search(r'(\d+)\s*(audio)?', message, re.IGNORECASE)
            if not match:
                 return False
            video_index = int(match.group(1)) - 1
            layi4_audio = bool(match.group(2))
            videos = self.search_results.get(thread_id, {}).get(author_id, [])
            if not videos or video_index < 0 or video_index >= len(videos):
                 return False
            video = videos[video_index]
            author_name = self.fetchUserInfo(author_id).changed_profiles.get(author_id, {}).get('zaloName', 'đéo xác định')
            video_id = video.get('video_id')
            author_info = video.get('author',{})
            author = author_info.get('nickname')
            author_id = author_info.get('unique_id')
            video_link = f"https://www.tiktok.com/@{author_id}/video/{video_id}"
            api_url = f'https://api.sumiproject.net/tiktok?video={video_link}'
            titlevd = video.get('title')
            load_msg = Message(text=f"Đang tải {'audio' if layi4_audio else 'video'}, chờ bé một xíu\n\n• Author: {author} [{author_id}]\n• Title: {titlevd}")
            self.replyMessage(load_msg, message_object, thread_id, thread_type, ttl=10000)
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            if 'data' not in data or 'play' not in data['data']:
                error_message = Message(text=f"Không thể lấy được link video từ API cho {video_link}.")
                self.replyMessage(error_message, message_object, thread_id, thread_type, ttl=60000)
                return True
            video_url = data['data']['play']
            titlevd = data['data']['title']
            messagesend = Message(text=f"[ {author_name} ]\n\n• Author: {author} [{author_id}]\n• Title: {titlevd}")
            thumbnail_url = data['data']['cover']
            if not layi4_audio:
                duration, width, height = self.get_video_info(video_url)
                self.sendRemoteVideo(
                    video_url,
                    thumbnail_url,
                    duration=duration,
                    message=messagesend,
                    thread_id=thread_id,
                    thread_type=thread_type,
                    ttl=86400000,
                    width=width,
                    height=height
                    )
        except requests.exceptions.RequestException as e:
            error_message = Message(text=f"Đã xảy ra lỗi khi gọi API: {str(e)}")
            self.replyMessage(error_message, message_object, thread_id, thread_type, ttl=60000)
            return True
        except Exception as e:
           logger.error(f"Lỗi trong quá trình xử lý: {e}")
           error_message = Message(text=f"Đã xảy ra lỗi không xác định: {str(e)}")
           self.replyMessage(error_message, message_object, thread_id, thread_type, ttl=60000)
           return True
    def cleanup_search_result(self, thread_id, author_id):
        if thread_id in self.search_result_messages and author_id in self.search_result_messages[thread_id]:
            del self.search_result_messages[thread_id][author_id]
            if not self.search_result_messages[thread_id]:
                del self.search_result_messages[thread_id]
        if thread_id in self.search_results and author_id in self.search_results[thread_id]:
             del self.search_results[thread_id][author_id]
             if not self.search_results[thread_id]:
                  del self.search_results[thread_id]

    def get_current_time(self):
        return time.time()
    def cleanup_expired_search_results(self):
         while True:
            time.sleep(60)
            now = self.get_current_time()
            
            for thread_id in list(self.search_result_messages):
                for author_id in list(self.search_result_messages[thread_id]):
                    search_result_info = self.search_result_messages[thread_id][author_id]
                    elapsed_time = now - search_result_info['time']
                    if elapsed_time > self.search_result_ttl:
                        self.cleanup_search_result(thread_id, author_id)

if __name__ == "__main__":
    try:
        client = Client(API_KEY, SECRET_KEY, IMEI, SESSION_COOKIES)
        client.listen(type="websocket", run_forever=True)
    except Exception as e:
        logger.error(f"Lỗi rồi, Không thể login...: {e}")
        python = sys.executable
        os.execl(python, python, *sys.argv)
        time.sleep(10) 
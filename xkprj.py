import os
import json
import importlib
import sys
import time
import threading
import re
from zlapi.models import Message
from config import ADMIN,PREFIX
from logging_utils import Logging
from colorama import Fore

sys.path.extend([
    os.path.dirname(os.path.abspath(__file__)),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules/auto'),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules/noprefix')
])
logger = Logging()

CACHE_DIR = 'modules/cache'
SETTINGS_FILE = 'seting.json'
DUYETBOX_FILE = os.path.join(CACHE_DIR, 'duyetboxdata.json')
DISABLED_THREADS_FILE = os.path.join(CACHE_DIR, 'disabled_threads.json')
RSEARCH_CMDS_FILE = os.path.join(CACHE_DIR, 'list_cmd_rsearch.json')
ALIAS_CMDS_FILE = os.path.join(CACHE_DIR, 'alias_commands.json')
MODULES_DIR = 'modules'
NOPREFIX_MODULES_DIR = 'modules/noprefix'
AUTO_MODULES_DIR = 'modules/auto'
def load_json(file_path, default=None):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {} if file_path.endswith(".json") else []

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

def adm():
    return load_json(SETTINGS_FILE).get('adm', [])

def admin():
    admin_id = load_json(SETTINGS_FILE).get('admin')
    if isinstance(admin_id, list):
        return admin_id
    else:
        return [admin_id] if admin_id else []

def prf():
    return load_json(SETTINGS_FILE).get('prefix')

def load_duyetbox_data():
    return load_json(DUYETBOX_FILE, [])

def load_disabled_threads():
    return load_json(DISABLED_THREADS_FILE, [])

def save_disabled_threads(disabled_threads):
    save_json(DISABLED_THREADS_FILE, disabled_threads)

def load_rsearch_commands():
   return load_json(RSEARCH_CMDS_FILE,{}).get('commands', [])

def save_rsearch_commands(commands):
    save_json(RSEARCH_CMDS_FILE, {'commands': commands})

def load_alias_commands():
    return load_json(ALIAS_CMDS_FILE, {}).get('aliases', {})

def save_alias_commands(aliases):
    save_json(ALIAS_CMDS_FILE, {'aliases': aliases})

class CommandHandler:
    def __init__(self, client):
        self.client = client
        self.vxkiue = self._load_modules(MODULES_DIR, 'ft_vxkiue', ['version', 'credits', 'description', 'power'])
        self.noprefix_vxkiue = self._load_modules(NOPREFIX_MODULES_DIR, 'ft_vxkiue', ['version', 'credits', 'description'])
        self.auto_vxkiue = self._load_auto_modules()
        self.disabled_threads = load_disabled_threads()
        self._admin_id = admin()
        self.rsearch_commands = load_rsearch_commands()
        self.alias_commands = load_alias_commands()
        self.current_prefix = prf()
        logger.prefixcmd(f"Prefix hiện tại của bot là '{self.current_prefix}'" if self.current_prefix else "Prefix hiện tại của bot là 'no prefix'")
        self._log_commands("alias", self.alias_commands)
        self._log_commands("re search", self.rsearch_commands)
        self.prefix_handlers = self._create_prefix_handlers()
    
    def _create_prefix_handlers(self):
       return sorted([(self.current_prefix + command, handler)
                       for command, handler in self.vxkiue.items() if self.current_prefix],
                       key=lambda item: len(item[0]), reverse=True)

    def _update_prefix(self):
        new_prefix = prf()
        if new_prefix != self.current_prefix:
            self.current_prefix = new_prefix
            logger.prefixcmd(f"Prefix đã được cập nhật thành '{self.current_prefix}'" if self.current_prefix else "Prefix đã được cập nhật thành 'no prefix'")
            self.prefix_handlers = self._create_prefix_handlers()

    def _log_commands(self, command_type, commands):
        if isinstance(commands, dict):
            if commands:
                log_text = f"Đã load thành công các {command_type}"
                logger.success(log_text.strip())
            else:
                logger.success(f"Không có {command_type} nào.")
        elif isinstance(commands, list):
            if commands:
                logger.success(f"Đã load thành công các lệnh {command_type}")
            else:
                 logger.success(f"Không có lệnh {command_type} nào.")

    def send_message(self, error_message, thread_id, thread_type):
        self.client.send(Message(text=error_message), thread_id, thread_type)

    def reply_message(self, error_message, message_object, thread_id, thread_type):
        self.client.replyMessage(Message(text=error_message), message_object, thread_id=thread_id, thread_type=thread_type, ttl=12000)

    def _load_modules(self, module_path, attribute_name, required_keys):
        modules, success_modules, failed_modules = {}, [], []
        for filename in os.listdir(module_path):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'{module_path.replace("/",".")}.{module_name}')
                    if hasattr(module, attribute_name) and hasattr(module, 'des') and all(key in module.des for key in required_keys):
                         modules.update(getattr(module, attribute_name)())
                         success_modules.append(module_name)
                    else:
                        failed_modules.append(module_name)
                except Exception as e:
                    logger.error(f"Không thể load được lệnh '{module_name}' trong {module_path}: {e}")
                    failed_modules.append(module_name)
        if success_modules:
            logger.success(f"Đã load thành công {len(success_modules)} lệnh trong {module_path}")
        if failed_modules:
            logger.warning(f"Không thể load được {len(failed_modules)} lệnh trong {module_path}: {', '.join(failed_modules)}")
        return modules

    def _load_auto_modules(self):
         auto_modules, success_auto, failed_auto = {}, [], []
         for filename in os.listdir(AUTO_MODULES_DIR):
             if filename.endswith('.py') and filename != '__init__.py':
                 module_name = filename[:-3]
                 try:
                    module = importlib.import_module(f'modules.auto.{module_name}')
                    if hasattr(module, 'start_auto'):
                        auto_modules[module_name] = module
                        success_auto.append(module_name)
                    else:
                        failed_auto.append(module_name)
                 except Exception as e:
                     logger.error(f"Không thể load được lệnh auto '{module_name}': {e}")
                     failed_auto.append(module_name)
         if success_auto:
             logger.success(f"Đã load thành công {len(success_auto)} lệnh auto")
             for module in success_auto:
                 threading.Thread(target=auto_modules[module].start_auto, args=(self.client,)).start()
         if failed_auto:
           logger.warning(f"Không thể load {len(failed_auto)} lệnh auto: {', '.join(failed_auto)}")
         return auto_modules

    def _handle_cmdrs(self, message, message_object, thread_id, thread_type, author_id):
        if author_id not in self._admin_id:
            self.reply_message("Bạn không có quyền quản lý lệnh re search.", message_object, thread_id, thread_type)
            return
        parts = message.split(self.current_prefix + 'cmdrs', 1)
        if len(parts) < 2:
            self.reply_message("Vui lòng sử dụng: .cmdrs [add|rmv|list] [command]", message_object, thread_id,thread_type)
            return
        command_part = parts[1].strip().lower()
        action, *target = command_part.split(' ', 1)
        target = target[0].strip() if target else None
        if not target and action != 'list':
           self.reply_message("Vui lòng sử dụng: .cmdrs [add|rmv|list] [command]", message_object, thread_id,thread_type)
           return
        if action == 'add':
            if target not in self.rsearch_commands:
                self.rsearch_commands.append(target)
                save_rsearch_commands(self.rsearch_commands)
                self._log_commands("re search", self.rsearch_commands)
                self.reply_message(f"Đã thêm lệnh '{target}' vào danh sách lệnh re search.", message_object, thread_id,thread_type)
            else:
                self.reply_message(f"Lệnh '{target}' đã có trong re search.", message_object, thread_id, thread_type)
        elif action == 'rmv':
            if target in self.rsearch_commands:
                self.rsearch_commands.remove(target)
                save_rsearch_commands(self.rsearch_commands)
                self._log_commands("re search", self.rsearch_commands)
                self.reply_message(f"Đã xóa lệnh '{target}' khỏi re search.", message_object, thread_id, thread_type)
            else:
                self.reply_message(f"Không tìm thấy lệnh '{target}' trong re search.", message_object, thread_id,thread_type)
        elif action == 'list':
            if self.rsearch_commands:
                self.reply_message(f"Các lệnh re search: {', '.join(self.rsearch_commands)}", message_object, thread_id,thread_type)
            else:
                self.reply_message("Không có lệnh re search nào.",message_object, thread_id,thread_type)
        else:
            self.reply_message("Vui lòng sử dụng: .cmdrs [add|rmv|list] [command]", message_object, thread_id,thread_type)

    def _handle_alias(self, message, message_object, thread_id, thread_type, author_id):
        if author_id not in self._admin_id:
            self.reply_message("Bạn không có quyền quản lý alias.", message_object, thread_id, thread_type)
            return
        parts = message.split(self.current_prefix + 'alias', 1)
        if len(parts) < 2:
            self.reply_message("Vui lòng sử dụng: .alias [add|rmv|list] [command] [alias]", message_object, thread_id,thread_type)
            return
        command_part = parts[1].strip().lower()
        action, *args = command_part.split(' ', 2)
        if not args and action != 'list':
            self.reply_message("Vui lòng sử dụng: .alias [add|rmv|list] [command] [alias]", message_object, thread_id,thread_type)
            return
        if action == 'add':
            if len(args) < 2:
                self.reply_message("Vui lòng sử dụng: .alias add <command> <alias>", message_object, thread_id, thread_type)
                return
            command, alias = args
            if command not in self.vxkiue:
                self.reply_message(f"Lệnh '{command}' không tồn tại.", message_object, thread_id, thread_type)
                return
            if command not in self.alias_commands:
                 self.alias_commands[command] = []
            if alias not in self.alias_commands[command]:
                self.alias_commands[command].append(alias)
                save_alias_commands(self.alias_commands)
                self._log_commands("alias", self.alias_commands)
                self.reply_message(f"Đã thêm alias '{alias}' cho lệnh '{command}'.", message_object, thread_id,thread_type)
            else:
                self.reply_message(f"Alias '{alias}' đã có cho lệnh '{command}'.", message_object, thread_id, thread_type)
        elif action == 'rmv':
            if len(args) < 2:
                 self.reply_message("Vui lòng sử dụng: .alias rmv <command> <alias>", message_object, thread_id, thread_type)
                 return
            command, alias = args
            if command not in self.alias_commands or alias not in self.alias_commands[command]:
                 self.reply_message(f"Không tìm thấy alias '{alias}' cho lệnh '{command}'.", message_object, thread_id, thread_type)
                 return
            self.alias_commands[command].remove(alias)
            if not self.alias_commands[command]:
                 del self.alias_commands[command]
            save_alias_commands(self.alias_commands)
            self._log_commands("alias", self.alias_commands)
            self.reply_message(f"Đã xóa alias '{alias}' khỏi lệnh '{command}'.", message_object, thread_id, thread_type)
        elif action == 'list':
             if self.alias_commands:
                 log_text = "Các alias hiện tại:\n"
                 for command, aliases in self.alias_commands.items():
                     if aliases:
                         log_text += f"{', '.join(aliases)} - {command}\n"
                 self.reply_message(log_text.strip(), message_object, thread_id, thread_type)
             else:
                 self.reply_message("Không có alias nào.", message_object, thread_id, thread_type)
        else:
            self.reply_message("Vui lòng sử dụng: .alias [add|rmv|list] [command] [alias]", message_object, thread_id,thread_type)
    def _get_content_message(self, message_object):
        if message_object.msgType == 'chat.sticker':
            return ""
        content = message_object.content
        if isinstance(content, dict) and 'title' in content:
            text_to_check = content['title']
        elif isinstance(content, str):
            text_to_check = content
        elif isinstance(content, dict) and 'href' in content:
            text_to_check = content['href']
        else:
            text_to_check = ""
        return text_to_check
    def _is_command_in_message(self, message_object):
        text_to_check = self._get_content_message(message_object)
        if not text_to_check or not text_to_check.startswith(self.current_prefix):
           return False
        message_parts = text_to_check.split(self.current_prefix, 1)
        if len(message_parts) < 2:
            return False
        command_part = message_parts[1].strip()
        if not command_part:
            return False
        command_name = command_part.split(' ')[0]
        if command_name in self.vxkiue:
            return True
        for command in self.rsearch_commands:
             if command_part.startswith(command) and re.match(rf"^{re.escape(command)}(\s|$)", command_part, re.IGNORECASE):
                return True
        for command, aliases in self.alias_commands.items():
             for alias in aliases:
                if command_part.startswith(alias) and re.match(rf"^{re.escape(alias)}(\s|$)", command_part, re.IGNORECASE):
                   return True
        return False
    def _execute_command(self, command_handler, message_text, message_object, thread_id, thread_type, author_id):
        try:
           command_handler(message_text, message_object, thread_id, thread_type, author_id, self.client)
        except Exception as e:
           self.reply_message(f"Lỗi khi thực hiện lệnh: {e}", message_object, thread_id, thread_type)
    def handle_command(self, message, author_id, message_object, thread_id, thread_type):
        self._update_prefix()
        message_text = self._get_content_message(message_object)
        if not message_text:
            return
        duyetbox_data = load_duyetbox_data()
        admins_list = adm() + admin()
        if thread_id not in duyetbox_data and author_id not in admins_list:
             if message_text.startswith(self.current_prefix):
                available_commands = list(self.vxkiue.keys())
                return
             noprefix_command_handler = self.noprefix_vxkiue.get(message_text.lower())
             if noprefix_command_handler:
               threading.Thread(target=self._execute_command, args=(noprefix_command_handler, message_text, message_object, thread_id, thread_type, author_id)).start()
             return
        if message_text.startswith(self.current_prefix + 'cmdrs'):
            threading.Thread(target=self._handle_cmdrs, args=(message_text, message_object, thread_id, thread_type, author_id)).start()
            return
        if message_text.startswith(self.current_prefix + 'alias'):
            threading.Thread(target=self._handle_alias, args=(message_text, message_object, thread_id, thread_type, author_id)).start()
            return
        noprefix_command_handler = self.noprefix_vxkiue.get(message_text.lower())
        if noprefix_command_handler:
            threading.Thread(target=self._execute_command, args=(noprefix_command_handler, message_text, message_object, thread_id, thread_type, author_id)).start()
            return
        if self.current_prefix:
            for prefix, handler in self.prefix_handlers:
                if message_text.lower().startswith(prefix):
                    self.client.sendReaction(messageObject=message_object, reactionIcon="/-ok", thread_id=thread_id,thread_type=thread_type)
                    threading.Thread(target=self._execute_command, args=(handler, message_text, message_object, thread_id, thread_type, author_id)).start()
                    return
        
        message_parts = message_text.split(self.current_prefix, 1)
        if len(message_parts) < 2:
            return
        command_part = message_parts[1].strip()
        if not command_part:
            return
        command_name = command_part.split(' ')[0]
        command_handler = self.vxkiue.get(command_name)
        if command_handler and message_text.startswith(self.current_prefix + command_name):
            self.client.sendReaction(messageObject=message_object, reactionIcon="/-ok", thread_id=thread_id,thread_type=thread_type)
            threading.Thread(target=self._execute_command, args=(command_handler, message_text, message_object, thread_id, thread_type, author_id)).start()
            return
        
        alias_matches = []
        for command, aliases in self.alias_commands.items():
            for alias in aliases:
                if command_part.startswith(alias) and re.match(rf"^{re.escape(alias)}(\s|$)", command_part, re.IGNORECASE):
                    alias_matches.append((alias, command))
        if alias_matches:
            alias_matches.sort(key=lambda x: len(x[0]), reverse=True)
            alias, command = alias_matches[0]
            self.client.sendReaction(messageObject=message_object, reactionIcon="/-ok", thread_id=thread_id,thread_type=thread_type)
            threading.Thread(target=self._execute_command, args=(self.vxkiue[command], message_text, message_object, thread_id, thread_type, author_id)).start()
            return
        
        rsearch_matches = []
        for command in self.rsearch_commands:
            if command in self.vxkiue and command_part.startswith(command) and re.match(rf"^{re.escape(command)}(\s|$)", command_part, re.IGNORECASE):
                rsearch_matches.append(command)
        if rsearch_matches:
           rsearch_matches.sort(key=len, reverse=True)
           command = rsearch_matches[0]
           self.client.sendReaction(messageObject=message_object, reactionIcon="/-ok", thread_id=thread_id,thread_type=thread_type)
           threading.Thread(target=self._execute_command, args=(self.vxkiue[command], message_text, message_object, thread_id, thread_type, author_id)).start()
           return

        if message_text.startswith(self.current_prefix):
            available_commands = list(self.vxkiue.keys())
            help_message = f"⋄ Sai Lệnh! Vui Lòng Chat: {self.current_prefix}menu hoặc {self.current_prefix}menu [số trang]" if available_commands else "Hiện tại chưa có lệnh nào được load. Vui lòng kiểm tra lại."
            self.reply_message(help_message, message_object, thread_id, thread_type)
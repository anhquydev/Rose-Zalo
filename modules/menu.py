from zlapi.models import Message, ZaloAPIException, MultiMsgStyle, MessageStyle
import time
import psutil
import os
import glob
import importlib
import json

des = {
    'version': "1.0.1",
    'credits': "Vũ Xuân Kiên",
    'description': "Lệnh menu",
    'power': "Thành viên"
}

start_time = time.time()

def get_commands_from_modules():
    module_dir = "modules"
    command_files = glob.glob(os.path.join(module_dir, "*.py"))
    commands = [os.path.splitext(os.path.basename(f))[0] for f in command_files]
    return commands

def get_all_vxkiue_with_info():
    vxkiue_info = {}

    for module_name in os.listdir('modules'):
        if module_name.endswith('.py') and module_name != '__init__.py':
            module_path = f'modules.{module_name[:-3]}'
            try:
                module = importlib.import_module(module_path)

                if hasattr(module, 'des'):
                    des = getattr(module, 'des')
                    version = des.get('version', 'Chưa có thông tin')
                    credits = des.get('credits', 'Chưa có thông tin')
                    description = des.get('description', 'Chưa có thông tin')
                    power = des.get('power', 'Chưa có thông tin')
                    vxkiue_info[module_name[:-3]] = (version, credits, description, power)
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")
                continue

    return vxkiue_info

def load_alias_commands():
    try:
        with open("modules/cache/alias_commands.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("aliases", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def handle_menu_command(message, message_object, thread_id, thread_type, author_id, client):
    vxkiue_info = get_all_vxkiue_with_info()
    alias_commands = load_alias_commands()
    items_per_page = 10
    args = message.split()
    current_page = 1
    if len(args) > 1:
       try:
          current_page = int(args[1])
       except ValueError:
           current_page = 1
    
    start_index = (current_page - 1) * items_per_page
    end_index = start_index + items_per_page
    total_pages = (len(vxkiue_info) + items_per_page - 1) // items_per_page
    menu_text = f"| Commands (Page {current_page}/{total_pages}):\n\n"
    for i, (command_name, (_, _, description, power)) in enumerate(list(vxkiue_info.items())[start_index:end_index]):
        aliases = alias_commands.get(command_name, [])
        alias_text = f" (Tên gọi khác: {', '.join(aliases)})" if aliases else ""
        menu_text += f"{start_index + i + 1}. {command_name}{alias_text} -> {description}\nQuyền hạn: {power}\n\n"

    client.replyMessage(Message(text=menu_text), message_object, thread_id, thread_type, ttl=300000)
    client.sendReaction(message_object, "Anh Quý Đẹp Trai", thread_id, thread_type)

def ft_vxkiue():
    return {
        'menu': handle_menu_command
    }
# modules/noprefix/sim.py

import requests
import urllib.parse
from zlapi.models import Message

des = {
    'version': "1.1.3",
    'credits': "Anh Quý & Nguyễn Đức Tài",
    'description': "Trả lời tự động khi người dùng gọi 'sim'",
    'power': "Thành viên"
}

def handle_noprefix_sim(message, message_object, thread_id, thread_type, author_id, client):
    if not isinstance(message, str):
        return  # Chỉ xử lý nếu là chuỗi

    lowered = message.lower().strip()

    # Nếu tin nhắn bắt đầu bằng "sim", "sim ơi", "sim à"
    if lowered.startswith("sim"):
        # Gỡ tiền tố
        content = lowered
        for prefix in ["sim ơi", "sim à", "sim"]:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
                break

        # Nếu không có nội dung hỏi thì nhắc người dùng
        if not content:
            client.sendMessage(Message(text="🗣️ Bạn muốn hỏi gì Sim nè?"), thread_id, thread_type)
            return

        # Encode và gọi API
        encoded = urllib.parse.quote(content, safe='')
        api_url = f"https://submxh.dichvudev.xyz/ai.php?reply={encoded}"

        try:
            res = requests.get(api_url, timeout=10)
            res.raise_for_status()
            data = res.json()

            reply_text = data.get("result", "❓ Sim không hiểu bạn nói gì...")

            client.replyMessage(
                Message(text=f"🤖 Sim: {reply_text}"),
                message_object,
                thread_id,
                thread_type,
                ttl=6000
            )

        except Exception as e:
            client.sendMessage(Message(text=f"⚠️ Sim bị lỗi: {str(e)}"), thread_id, thread_type)

# Hàm bắt buộc để bot load module noprefix
def ft_vxkiue():
    return {
        '*': handle_noprefix_sim  # '*' để bắt toàn bộ tin nhắn trong chế độ noprefix
    }

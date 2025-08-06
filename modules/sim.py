from zlapi.models import Message
import requests
import urllib.parse

des = {
    'version': "3.1.0",
    'credits': "Anh Quý",
    'description': "Sim trả lời tự nhiên khi được gọi bằng từ khóa như 'sim', 'shin', 'bạn ơi' hoặc khi được reply",
    'power': "Thành viên"
}

# Danh sách các từ khóa để kích hoạt sim
KEYWORDS = ["sim", "shin", "bạn ơi", "bot", "chị ơi", "em ơi", "sim ơi", "shin ơi"]

# Kiểm tra xem tin nhắn có gọi sim không
def is_sim_called(message):
    lower = message.lower()
    return any(keyword in lower for keyword in KEYWORDS)

# Gửi tin đến API AI
def get_ai_reply(user_input):
    try:
        encoded = urllib.parse.quote(user_input, safe='')
        api_url = f"https://submxh.dichvudev.xyz/ai.php?reply={encoded}"
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return data.get("result", "Sim đang bận suy nghĩ nè...")
    except:
        return "Sim bị lag rồi đó..."

# Hàm xử lý chính
def handle_sim(message, message_object, thread_id, thread_type, author_id, client):
    # Nếu chứa từ khóa gọi sim
    if is_sim_called(message):
        reply = get_ai_reply(message)
        client.sendMessage(Message(text=reply), thread_id, thread_type, ttl=6000000000000)
        return

    # Nếu đang reply tin nhắn của sim
    if message_object.reply_message:
        replied_msg = message_object.reply_message.text.lower()
        if any(k in replied_msg for k in KEYWORDS):
            reply = get_ai_reply(message)
            client.sendMessage(Message(text=reply), thread_id, thread_type, ttl=60000000000000)
            client.sendReaction(message_object, "Bucu", thread_id, thread_type)

def ft_vxkiue():
    return {
        '': handle_sim
    }
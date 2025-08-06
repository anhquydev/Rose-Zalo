from config import PREFIX
from zlapi.models import Message
import json, time

des = {
    'version': "1.0.5",
    'credits': "Anh Quý",
    'description': "check prefix",
    'power': "Thành viên"
}

def prf():
    with open('seting.json', 'r') as f:
        return json.load(f).get('prefix')

def checkprefix(message, message_object, thread_id, thread_type, author_id, client):
    gui = Message(text=f"🔎 Bot By Anh Quý \n⚙️ Prefix của bot là: 「 {prf()} 」")
    client.replyMessage(gui, message_object, thread_id, thread_type, ttl=5000000000)

def ft_vxkiue():
    return {
        'prefix': checkprefix
    }
    
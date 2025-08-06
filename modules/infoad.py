import json
import random
from zlapi import ZaloAPI, ZaloAPIException
from zlapi.models import *
import os

des = {
    'version': "1.0.0",
    'credits': "Vũ Xuân Kiên",
    'description': "Thông tin Admin",
    'power': "Thành viên"
}

def random_img():
    folder_path = r'modules/cache'
    all_files = os.listdir(folder_path)
    image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not image_files:
        return None
    random_image = random.choice(image_files)
    return os.path.join(folder_path, random_image)

def handle_infoad(message, message_object, thread_id, thread_type, author_id, bot):
    img =random_img()
    msg = (
        f"🌟 Chào Mừng Đến Với Vũ Xuân Kiên! 🎉\n"
        f"👨‍💻 Tên: Vũ Xuân Kiên\n"
        f"🐳 Biệt Danh: Vxkiue\n"
        f"🎂 Ngày Sinh: 12/12/2009\n"
        f"⚧ Giới Tính: Nam\n"
        f"📲 Facebook: https://www.facebook.com/vuxuankiendzvcl\n"
        f"✉️ Email: vxkiue@gmail.com\n"
        f"🌈 Giới Thiệu Về Tôi:\n"
        f"Xin chào! Tôi là Vũ Xuân Kiên, biệt danh Vxkiue, một người đam mê công nghệ 💻 và là tác giả của bot này 🤖. Tôi yêu thích khám phá công nghệ mới và tạo ra những ứng dụng hữu ích cho cộng đồng 🌍\n"
        f"📩 Liên Hệ:\n"
        f"Nếu bạn có câu hỏi hoặc cần hỗ trợ, hãy gửi tin nhắn cho tôi! Tôi luôn sẵn sàng giúp đỡ 🤝\n"
        f"🛡️ Bản Quyền: © Admin Bot VXK"
    )

    bot.sendLocalImage(img, thread_id=thread_id, thread_type=thread_type, width=2560, height=2560, message=Message(text=msg))

def ft_vxkiue():
    return {
        'infoad': handle_infoad
    }
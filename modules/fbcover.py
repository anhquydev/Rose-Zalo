import os
import requests
from zlapi.models import Message, Mention

des = {
    'version': "1.0.2",
    'credits': "Vũ Xuân Kiên",
    'description': "Tạo ảnh bìa Facebook giả",
    'power': "Thành viên"
}

CACHE_DIR = 'modules/cache'
os.makedirs(CACHE_DIR, exist_ok=True)

def get_fake_fb_cover(name, uid, address, email, subname, sdt, color):
    url = f"https://subhatde.id.vn/fbcover/v1?name={name}&uid={uid}&address={address}&email={email}&subname={subname}&sdt={sdt}&color={color}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_path = os.path.join(CACHE_DIR, "fake_fb_cover.png")
            with open(image_path, 'wb') as file:
                file.write(response.content)
            return image_path
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

def handle_fake_fb_cover_command(message, message_object, thread_id, thread_type, author_id, client):
    content = message[len("!fbcover "):].strip().split('|')
    if len(content) < 7:
        error_message = Message(text="Lỗi! Vui lòng nhập thông tin đầy đủ theo định dạng:\nname|uid|address|email|subname|sdt|color")
        client.replyMessage(error_message, message_object, thread_id, thread_type, ttl=60000)
        return

    name = content[0].strip()
    uid = content[1].strip()
    address = content[2].strip()
    email = content[3].strip()
    subname = content[4].strip()
    sdt = content[5].strip()
    color = content[6].strip()

    loading_message = Message(text="Đang tạo ảnh bìa Facebook giả... Vui lòng chờ 1-3s.")
    client.replyMessage(loading_message, message_object, thread_id, thread_type, ttl=60000)

    image_path = get_fake_fb_cover(name, uid, address, email, subname, sdt, color)

    if image_path:
        success_message = Message(
            text=f"@Fbcover, ảnh bìa Facebook giả của bạn đã được tạo với các thông tin:\n"
                 f"Tên: {name}\nUID: {uid}\nĐịa chỉ: {address}\nEmail: {email}\nBiệt danh: {subname}\nSĐT: {sdt}\nMàu sắc: {color}\n> [ Vu Xuan Kien ]",
            mention=Mention(author_id, length=len(f"@Fbcover"), offset=0)
        )
        client.sendLocalImage(
            imagePath=image_path,
            message=success_message,
            thread_id=thread_id,
            thread_type=thread_type,
            width=2553,
            height=945,
            ttl=86400000
        )
        os.remove(image_path)
    else:
        error_message = Message(text="❌ Đã xảy ra lỗi khi tạo ảnh bìa. Vui lòng thử lại.")
        client.replyMessage(error_message, message_object, thread_id, thread_type)

def ft_vxkiue():
    return {
        'fbcover': handle_fake_fb_cover_command,
    }

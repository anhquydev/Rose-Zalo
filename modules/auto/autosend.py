import time
import random
import requests
from zlapi.models import Message, ThreadType
from datetime import datetime, timedelta
import pytz
import ffmpeg
import json
import os
import uuid
from logging_utils import Logging
import traceback
logger = Logging()

time_messages = {
    "05:05": ["Thức dậy để đón ngày mới tuyệt vời nào! ✨", "vdchill"],
    "06:05": ["Chào ngày mới, bạn đã sẵn sàng chưa? 💪", "vdchill"],
    "07:05": ["Bắt đầu ngày mới với một bữa sáng ngon lành nhé! 🍳", "vdgirl"],
    "09:05": ["Làm gì đó cho vui lên bạn ơi! 🎉", "vdgirl"],
    "11:05": ["Đến giờ nạp năng lượng rồi, ăn trưa thôi! 🍔", "vdgirl"],
    "13:05": ["Nghỉ ngơi chút rồi tiếp tục nha! ☕", "vdchill"],
    "15:05": ["Chiều đến rồi, làm gì đó thú vị nào! 🌇", "vdgirl"],
    "17:05": ["Kết thúc một ngày rồi, thư giãn thôi! 🛀", "nhac"],
    "18:05": ["Ăn tối vui vẻ cùng người thân nhé! 👨‍👩‍👧‍👦", "nhac"],
    "20:18": ["Thời gian cho riêng mình, tận hưởng đi! 🧘", "nhac"],
    "21:05": ["Chuẩn bị cho giấc ngủ ngon nhé bạn! 🛌", "nhac"],
    "22:05": ["Ngủ ngon nha, mai có nhiều điều mới! 🌃", "nhac"],
    "23:05": ["Ngủ sớm để khỏe bạn nhé! 😴", "vdchill"],
}

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
IMGUR_CLIENT_ID = "85a847235508ec9"

video_captions = {
    "vdchill": "Chill một chút!!! 😌",
    "vdgirl": "Cung cấp vitamin gái cho anh em đây!!! 😍",
    "vdanime": "Giải trí cùng một video anime nhé!!! 🌸",
    "nhac": "Thưởng thức âm nhạc cùng một bài nhạc rất hot trên Youtube!!! 🎶"
}

def get_video_info(video_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            probe = ffmpeg.probe(video_url)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if not video_stream:
                 raise ValueError("Không tìm thấy luồng video trong URL")

            duration = float(video_stream['duration']) * 1000
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            return duration, width, height
        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video (lần {attempt + 1}/{max_retries}): {str(e)}", exc_info=True)
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Đợi {wait_time} giây trước khi thử lại...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Không thể lấy thông tin video sau nhiều lần thử: {str(e)}") from e

def load_allowed_groups():
    try:
        with open("modules/cache/sendtask_autosend.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("allowed_groups.json not found. Creating an empty one.")
        return {"groups": []}
    except json.JSONDecodeError:
        logger.error("Error decoding allowed_groups.json. Returning an empty list.", exc_info=True)
        return {"groups": []}

def load_video_data(folder_path):
  video_data = {}
  for filename in os.listdir(folder_path):
      if filename.endswith(".json"):
          file_key = filename[:-5]
          file_path = os.path.join(folder_path, filename)
          try:
              with open(file_path, "r") as f:
                data = json.load(f)
                if isinstance(data,list):
                   video_data[file_key]=data
                else:
                    logger.error(f"File {filename} is not in correct format.  It should be a JSON list of video URLs.")
                    video_data[file_key] = []
          except Exception as e:
              logger.error(f"Error loading {filename}: {e}", exc_info=True)
              video_data[file_key] = []
  return video_data

def start_auto(client):
    try:
        video_folder = "modules/cache/data"
        video_data = load_video_data(video_folder)
        allowed_groups_data = load_allowed_groups()
        allowed_thread_ids = allowed_groups_data.get("groups", [])
        last_sent_time = None
        while True:
            now = datetime.now(vn_tz)
            current_time_str = now.strftime("%H:%M")
            if current_time_str in time_messages:
                if last_sent_time is None or now - last_sent_time >= timedelta(minutes=1):
                  message_data = time_messages[current_time_str]
                  message = message_data[0]
                  video_source = message_data[1] if len(message_data) > 1 else None

                  if not video_source or video_source not in video_data:
                      available_video_sources = [key for key in video_data if video_data[key]]
                      if not available_video_sources:
                          logger.warning("No videos available in any source.")
                          time.sleep(30)
                          continue
                      video_source = random.choice(available_video_sources)

                  videos = video_data.get(video_source, [])

                  if not videos:
                      logger.warning(f"No videos found for source: {video_source}")
                      time.sleep(30)
                      continue

                  video_url = random.choice(videos)
                  if not video_url:
                      logger.warning(f"No URL found for video in source {video_source}.")
                      time.sleep(30)
                      continue
                  try:
                      duration, width, height = get_video_info(video_url)
                  except Exception as e:
                      logger.error(f"Error getting video info for {video_url}: {e}", exc_info=True)
                      time.sleep(30)
                      continue

                  for thread_id in allowed_thread_ids:
                      final_message = f"{current_time_str} | {message}\n\n{video_captions.get(video_source, 'Video')}"
                      gui = Message(text=final_message)
                      try:
                          client.sendRemoteVideo(
                              video_url,
                              None,
                              duration=duration,
                              message=gui,
                              thread_id=thread_id,
                              thread_type=ThreadType.GROUP,
                              width=width,
                              height=height,
                              ttl=1800000
                          )
                          time.sleep(0.3)
                      except Exception as e:
                          logger.error(f"Error sending message to {thread_id}: {e}", exc_info=True)
                  last_sent_time = now
            time.sleep(30)

    except Exception as e:
        logger.error(f"Error in start_auto: {e}", exc_info=True)
        raise e
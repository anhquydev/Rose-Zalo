import json
import os

# --- HÀM HỖ TRỢ ---

def read_setting_value(key):
    try:
        with open('seting.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings.get(key)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️ Không thể đọc seting.json. Dùng giá trị mặc định.")
        return None

def read_prefix():
    return read_setting_value('prefix') or "."

def read_admin():
    admin_data = read_setting_value('admin')
    if isinstance(admin_data, list):
        return [str(i) for i in admin_data if i]
    elif isinstance(admin_data, str):
        return [admin_data]
    else:
        return []

# --- CẤU HÌNH ---

PREFIX = read_prefix()
ADMIN = read_admin()
if not ADMIN:
    ADMIN = ["3586564051212905001"]

# --- THÔNG TIN KHÁC ---
IMEI = "7e3e704b-7459-43ce-a6aa-01085674b145-cd5d5f3ff8f374827248e13d2f7d64ca"
SESSION_COOKIES = {"_ga":"GA1.2.1396050420.1752150524","_ga_VM4ZJE1265":"GS2.2.s1752150524$o1$g0$t1752150524$j60$l0$h0","ozi":"2000.QOBlzDCV2uGerkFzm09HsMRSulp52rVHBTtb-8iBLTGgtkdmE3C.1","_gid":"GA1.2.724299456.1753652399","_zlang":"vn","zpsid":"Vibt.422239794.11.GQ71xPQpo_caRU7WchFB-UF0kSsaWVdAhuJopPU4HQcaGkbObrXLV_wpo_a","zpw_sek":"35eA.422239794.a0.FgpragFp_gMHBTIyWlF-fTZHcyw1oTpAwiA9qUIYX_pvm8YEvQ2KuFUQXj34piE7tlB9A_F13uS2yXKx9Pl-fG","__zi":"3000.SSZzejyD6zOgdh2mtnLQWYQN_RAG01ICFjIXe9fEM8Wyc--daKjJZtcTuQRVIr6AVfxjhZWp.1","__zi-legacy":"3000.SSZzejyD6zOgdh2mtnLQWYQN_RAG01ICFjIXe9fEM8Wyc--daKjJZtcTuQRVIr6AVfxjhZWp.1","app.event.zalo.me":"1071601323465243734","_ga_RYD7END4JE":"GS2.2.s1753652399$o2$g1$t1753653587$j60$l0$h0"}

API_KEY = 'api_key'
SECRET_KEY = 'secret_key'
PREFIX = read_prefix() or "."
ADMIN = read_admin()
if ADMIN is None:
    ADMIN = []
elif not isinstance(ADMIN, list):
    ADMIN = [ADMIN]
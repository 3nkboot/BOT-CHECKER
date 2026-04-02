# config.py
import os

# توكن البوت
TOKEN = "8574162513:AAHsiVcsrNKe0CayTbdlSHKfUFwB_5JbIUw"

# ID الادمن (حط معرفك)
ADMIN_ID = 7533168895  # غير هذا برقمك

# إعدادات API
API_URL = "https://api.chkr.cc/"
MAX_CONCURRENT = 5
RATE_DELAY = 0.5
RETRY_COUNT = 3

# إعدادات البروكسيات
USE_PROXY = True
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
]

# إعدادات قاعدة البيانات
DB_FILE = "bot_data.db"

# إعدادات الملفات
TEMP_DIR = "temp_files"
RESULTS_DIR = "results"

# إنشاء المجلدات
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
# حالة البوت (مقفل أو مفتوح)
BOT_LOCKED = False
# بروكسيات مدفوعة (مخفية)
PAID_PROXIES = [
    "http://rjcjococ:ymfjq63sp671@23.95.150.145:6114",
    "http://rjcjococ:ymfjq63sp671@107.172.163.27:6543",
]
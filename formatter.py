# formatter.py
from datetime import datetime

def format_live_card(card_str: str, result: dict):
    """تنسيق البطاقة الحية"""
    card_info = result.get("card", {})
    card_parts = card_str.split('|')

    card_number = card_parts[0]
    month = card_parts[1] if len(card_parts) > 1 else "XX"
    year = card_parts[2] if len(card_parts) > 2 else "XX"
    cvv = card_parts[3] if len(card_parts) > 3 else "XXX"

    bank = card_info.get("bank", "Unknown Bank")
    card_type = card_info.get("type", "UNKNOWN").upper()
    category = card_info.get("category", "UNKNOWN").upper()
    country = card_info.get("country", {}).get("name", "Unknown")
    country_emoji = card_info.get("country", {}).get("emoji", "🌍")
    
    full_card = f"{card_number}|{month}|{year}|{cvv}"

    return f"""
# 🌟
- - - - - - - - - - - - - - - - - - - - - - -
📋 **لنسخ البطاقة اضغط على الرقم أدناه:**
`{full_card}`
- - - - - - - - - - - - - - - - - - - - - - -
ϟ 𝐒𝐭𝐚𝐭𝐮𝐬: Approved! ✅
ϟ 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: Insufficient Funds
- - - - - - - - - - - - - - - - - - - - - - -
ϟ 𝐁𝐢𝐧: {card_type} - {category}
ϟ 𝐁𝐚𝐧𝐤: {bank} - {country_emoji}
ϟ 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country.upper()} [ {country_emoji} ]
- - - - - - - - - - - - - - - - - - - - - - -
⌥ 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: @ayoubbbbbbbbl
⌥ 𝐆𝐚𝐭𝐞 𝐏𝐫𝐢𝐜𝐞:
- - - - - - - - - - - - - - - - - - - - - - -
⌤ 𝐃𝐞𝐯 𝐛𝐲: @ayoubbbbbbbbl - 🍀
"""

def format_welcome_message(user_data):
    """تنسيق رسالة الترحيب"""
    user_id = user_data.get("user_id", "Unknown")
    username = user_data.get("username", "")
    name = user_data.get("name", "")
    subscription = "✅ Active" if user_data.get("subscription") else "❌ Not Subscribed"
    points = user_data.get("points", 0)
    
    if username and username != "Unknown":
        display_name = username
    elif name:
        display_name = name
    else:
        display_name = str(user_id)

    return f"""
- - - - - - - - - - - - - - - - - - - - - - -
👋 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 @{display_name}! 🔥
- - - - - - - - - - - - - - - - - - - - - - -
📊 𝐘𝐨𝐮𝐫 𝐒𝐭𝐚𝐭𝐮𝐬:
👤 𝐍𝐚𝐦𝐞: {display_name}
🆔 𝐈𝐃: {user_id}
⏰ 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧: {subscription}
💎 𝐏𝐨𝐢𝐧𝐭𝐬: {points}
- - - - - - - - - - - - - - - - - - - - - - -
[⌤] 𝐃𝐞𝐯 𝐛𝐲: @ayoubbbbbbbbl - 🍀
"""

def format_stats_message(stats):
    """تنسيق رسالة الإحصائيات"""
    bar = format_progress_bar(stats["completed"], stats["total"])
    percent = (stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0

    return f"""
╔════════════════════════════════════════════╗
║           🔥 CHK BOT 🔥
╠════════════════════════════════════════════╣
║ 📁 File: {stats['file_name']}
║ 📦 Size: {stats['file_size']}
╠════════════════════════════════════════════╣
║ 🔄 Progress: {percent:.1f}%
║ [{bar}]
║ ⏱️ Elapsed: {stats['elapsed']} | ETA: {stats['eta']}
╠════════════════════════════════════════════╣
║ ✅ LIVE: {stats['live']}
║ ❌ DECLINED: {stats['declined']}
║ ⚠️ UNKNOWN: {stats['unknown']}
║ 📊 TOTAL: {stats['completed']}/{stats['total']}
╚════════════════════════════════════════════╝
"""

def format_progress_bar(completed, total, width=25):
    if total == 0:
        return "░" * width
    percent = completed / total
    filled = int(width * percent)
    return "█" * filled + "░" * (width - filled)

def format_admin_menu():
    """قائمة الادمن"""
    return """
╔══════════════════════════════╗
║      🔧 Admin Panel 🔧
╠══════════════════════════════╣
║ 🔓 /unlock - فتح البوت
║ 🔒 /lock - قفل البوت
║ ➕ /addpoints [id] [points]
║ 🎫 /addsub [id] [days]
║ 📊 /users - إحصائيات
║ 📁 /files [id] - ملفات مستخدم
║ 🔄 /update_proxies - تحديث بروكسيات
║ 📤 /export_live - تصدير اللايف
╚══════════════════════════════╝
"""

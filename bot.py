import requests
import time
import logging
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت
BOT_TOKEN = ('8574162513:AAFuxhjffUh9tP8LzDAnLostStEJV2nOkRA')
ALLOWED_USER_ID = os.environ.get('ALLOWED_USER_ID')

if not BOT_TOKEN:
    logger.error("❌ لم يتم تعيين BOT_TOKEN")
    sys.exit(1)

logger.info("✅ تم تحميل التوكن بنجاح")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # """رسالة البداية"""
    user = update.effective_user
    text = (
        f"👋 مرحباً {user.first_name}!\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "/check [بطاقة] - فحص بطاقة واحدة\n"
        "/help - عرض المساعدة\n\n"
        "📎 **فحص ملف:** ارفع ملف .txt"
    )
    await update.message.reply_text(text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""مساعدة البوت"""
    text = (
        "🆘 **المساعدة**\n\n"
        "**🔹 فحص بطاقة واحدة:**\n"
        "/check 4111111111111111|12|25|123\n\n"
        "**🔹 فحص ملف:**\n"
        "1. ارفع ملف .txt\n"
        "2. كل بطاقة في سطر منفصل\n"
        "3. الصيغة: رقم|شهر|سنة|cvv\n\n"
        "**مثال محتوى الملف:**\n"
        "4111111111111111|12|25|123\n"
        "5111111111111111|11|24|456\n"
        "371111111111111|10|26|789"
    )
    await update.message.reply_text(text)

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # """فحص بطاقة واحدة"""
    user = update.effective_user
    
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ غير مصرح لك")
    
    # التحقق من وجود البطاقة
    if not context.args:
        return await update.message.reply_text("❌ استخدم: /check رقم|شهر|سنة|cvv")
    
    card = ' '.join(context.args).strip()
    
    # التحقق من الصيغة
    if not validate_card(card):
        return await update.message.reply_text("❌ صيغة البطاقة غير صحيحة")
    
    msg = await update.message.reply_text("🔄 جاري الفحص...")
    
    try:
        result = check_card(card)
        emoji = "✅" if "موافقة" in result else "❌"
        response = f"{emoji} **النتيجة:** {result}\n`{mask_card(card)}`"
        await msg.edit_text(response)
    except Exception as e:
        await msg.edit_text(f"❌ خطأ: {str(e)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #"""معالجة الملفات"""
    user = update.effective_user
    
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ غير مصرح لك")
    
    # التحقق من وجود ملف
    if not update.message.document:
        return
    
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    
    # التحقق من نوع الملف
    if not file_name.endswith('.txt'):
        return await update.message.reply_text("❌ يرجى رفع ملف .txt فقط")
    
    status = await update.message.reply_text("📥 جاري التحميل...")
    
    try:
        # تحميل الملف
        file_path = f"/tmp/{file_name}"
        await file.download_to_drive(file_path)
        
        # قراءة الملف
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # حذف الملف
        os.remove(file_path)
        
        # استخراج البطاقات الصحيحة
        cards = []
        for line in lines:
            card = line.strip()
            if card and validate_card(card):
                cards.append(card)
        
        if not cards:
            return await status.edit_text("❌ لا توجد بطاقات صحيحة")
        
        await status.edit_text(f"✅ {len(cards)} بطاقة صحيحة\n🔄 جاري الفحص...")
        
        # فحص البطاقات
        approved = 0
        declined = 0
        errors = 0
        
        for i, card in enumerate(cards):
            try:
                result = check_card(card)
                if "موافقة" in result:
                    approved += 1
                elif "رفض" in result:
                    declined += 1
                else:
                    errors += 1
            except:
                errors += 1
            
            # تحديث كل 20 بطاقة
            if (i + 1) % 20 == 0:
                await status.edit_text(f"📊 تم فحص {i+1}/{len(cards)}")
        
        # النتيجة النهائية
        result_text = (
            f"📊 **نتيجة الفحص**\n"
            f"📄 الملف: {file_name}\n"
            f"📝 المجموع: {len(cards)}\n"
            f"✅ مقبول: {approved}\n"
            f"❌ مرفوض: {declined}\n"
            f"⚠️ أخطاء: {errors}"
        )
        
        if approved > 0:
            result_text += f"\n📈 نسبة النجاح: {(approved/len(cards)*100):.1f}%"
        
        await update.message.reply_text(result_text)
        
    except Exception as e:
        logger.error(f"خطأ: {e}")
        await status.edit_text(f"❌ حدث خطأ: {str(e)}")

def validate_card(card):
   # """التحقق من صحة البطاقة"""
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return False
        
        number, month, year, cvv = [p.strip() for p in parts]
        
        # فحص رقم البطاقة
        if not number.isdigit() or len(number) < 15 or len(number) > 16:
            return False
        
        # فحص الشهر
        if not month.isdigit() or int(month) < 1 or int(month) > 12:
            return False
        
        # فحص السنة
        if not year.isdigit():
            return False
        if len(year) == 4:
            year = year[2:]
        if len(year) != 2:
            return False
        
        # فحص CVV
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            return False
        
        return True
    except:
        return False

def check_card(card):
 #   """فحص البطاقة"""
    try:
        parts = card.split('|')
        number = parts[0].strip()
        
        # محاكاة وقت الفحص
        time.sleep(0.2)
        
        # تحديد نوع البطاقة
        if number.startswith('4'):
            return "✅ موافقة - فيزا"
        elif number.startswith('5'):
            return "✅ موافقة - ماستركارد"
        elif number.startswith('3'):
            return "✅ موافقة - امريكان اكسبريس"
        elif number.startswith('6'):
            return "✅ موافقة - ديسكفر"
        else:
            return "❌ رفض - نوع غير معروف"
    except:
        return "⚠️ خطأ في الفحص"

def mask_card(card):
   # """إخفاء رقم البطاقة"""
    try:
        parts = card.split('|')
        number = parts[0]
        if len(number) > 8:
            masked = number[:6] + "******" + number[-4:]
            return f"{masked}|{parts[1]}|{parts[2]}|{parts[3]}"
        return card
    except:
        return card

def main():
    #"""تشغيل البوت"""
    logger.info("🚀 بدء تشغيل البوت...")
    
    try:
        # إنشاء التطبيق
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة المعالجات
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("check", check_single))
        app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        
        logger.info("✅ البوت جاهز للعمل!")
        
        # بدء البوت
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل التشغيل: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

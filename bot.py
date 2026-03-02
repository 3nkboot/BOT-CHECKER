import requests
import base64
import re
import time
import logging
import os
import sys
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError

# إعداد التسجيل بشكل أكثر تفصيلاً
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# توكن البوت من المتغيرات البيئية
BOT_TOKEN = os.environ.get('8574162513:AAFTl0hvQFaCKjynyQorpOEfKk_z1nN1YpA')

# معرف المشرف المسموح له باستخدام البوت (اختياري)
ALLOWED_USER_ID = os.environ.get('ALLOWED_USER_ID')

# التحقق من وجود التوكن
if not BOT_TOKEN:
    logger.error("❌ لم يتم تعيين BOT_TOKEN. يرجى تعيينه في المتغيرات البيئية.")
    sys.exit(1)

logger.info(f"✅ تم تحميل التوكن بنجاح: {BOT_TOKEN[:5]}...")

# جلسة requests عامة
r = requests.Session()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    user = update.effective_user
    logger.info(f"📱 مستخدم جديد: {user.id} - {user.first_name}")
    
    try:
        welcome_text = (
            f"👋 مرحباً {user.first_name}!\n\n"
            f"✅ البوت يعمل بنجاح!\n\n"
            f"📊 معلومات البوت:\n"
            f"• المعرف: {user.id}\n"
            f"• الاسم: {user.first_name}\n"
            f"• الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔹 استخدم /help لعرض الأوامر المتاحة"
        )
        
        await update.message.reply_text(welcome_text)
        logger.info(f"✅ تم إرسال رسالة الترحيب للمستخدم {user.id}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في دالة start: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    user = update.effective_user
    logger.info(f"📱 أمر help من المستخدم: {user.id}")
    
    help_text = (
        "🆘 **مساعدة البوت**\n\n"
        "**الأوامر المتاحة:**\n"
        "/start - بدء التشغيل\n"
        "/help - عرض هذه المساعدة\n"
        "/ping - اختبار الاتصال\n"
        "/check [بطاقة] - فحص بطاقة واحدة\n\n"
        "**صيغة البطاقة:**\n"
        "رقم|شهر|سنة|cvv\n"
        "مثال: `/check 4111111111111111|12|25|123`\n\n"
        "⚠️ **تحذير**: هذا البوت للأغراض التعليمية فقط"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اختبار الاتصال"""
    user = update.effective_user
    logger.info(f"📱 أمر ping من المستخدم: {user.id}")
    
    start_time = time.time()
    await update.message.reply_text("🏓 جاري اختبار الاتصال...")
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000
    await update.message.reply_text(f"🏓 **بونغ!**\n⏱️ وقت الاستجابة: {response_time:.2f} مللي ثانية", parse_mode='Markdown')

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فحص بطاقة واحدة"""
    user = update.effective_user
    logger.info(f"📱 أمر check من المستخدم: {user.id}")
    
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من وجود البطاقة
    if not context.args:
        await update.message.reply_text(
            "❌ يرجى إدخال البطاقة\n"
            "مثال: `/check 4111111111111111|12|25|123`"
        )
        return
    
    card = ' '.join(context.args).strip()
    logger.info(f"💳 فحص بطاقة: {card[:10]}...")
    
    # التحقق من الصيغة
    if not validate_card_format(card):
        await update.message.reply_text(
            "❌ صيغة غير صحيحة\n"
            "الصيغة: رقم|شهر|سنة|cvv\n"
            "مثال: 4111111111111111|12|25|123"
        )
        return
    
    status_msg = await update.message.reply_text("🔄 جاري الفحص...")
    
    try:
        result = m3_iw(card)
        logger.info(f"✅ نتيجة الفحص: {result}")
        
        emoji = "✅" if "Charge !" in result else "❌"
        
        response = (
            f"{emoji} **النتيجة**\n\n"
            f"💳 البطاقة: `{card}`\n"
            f"📊 الحالة: {result}"
        )
        
        await status_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ خطأ في الفحص: {str(e)}")
        await status_msg.edit_text(f"❌ خطأ: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"❌ حدث خطأ: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
            )
    except:
        pass

def validate_card_format(card):
    """التحقق من صيغة البطاقة"""
    parts = card.split('|')
    if len(parts) != 4:
        return False
    if not all(parts):
        return False
    if not parts[0].isdigit():
        return False
    return True

def m3_iw(ccx):
    """دالة الفحص مع تحسين معالجة الأخطاء"""
    try:
        ccx = ccx.strip()
        parts = ccx.split("|")
        
        if len(parts) != 4:
            return "خطأ: صيغة البطاقة غير صحيحة"
            
        n = parts[0].strip()
        mm = parts[1].strip()
        yy = parts[2].strip()
        cvc = parts[3].strip()

        # التحقق من صحة البيانات
        if not n.isdigit() or len(n) < 15:
            return "خطأ: رقم البطاقة غير صحيح"
            
        if not mm.isdigit() or int(mm) < 1 or int(mm) > 12:
            return "خطأ: الشهر غير صحيح"
            
        # معالجة السنة
        if "20" in yy:
            yy = yy.split("20")[1]
        if not yy.isdigit() or len(yy) != 2:
            return "خطأ: السنة غير صحيحة"
            
        if not cvc.isdigit() or len(cvc) < 3:
            return "خطأ: الرقم السري غير صحيح"
        
        # هنا يمكنك إضافة كود الفحص الفعلي
        time.sleep(1)  # محاكاة وقت الفحص
        
        # نتائج تجريبية للاختبار
        if n.startswith('4'):
            return "✅ Charge ! (تمت الموافقة)"
        elif n.startswith('5'):
            return "⚠️ بطاقة ماستركارد - تحتاج فحص إضافي"
        else:
            return "❌ تم الرفض - بطاقة غير مدعومة"
        
    except Exception as e:
        logger.error(f"خطأ في m3_iw: {str(e)}")
        return f"خطأ في الفحص: {str(e)}"

def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت...")
    
    try:
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ تم إنشاء تطبيق البوت")
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("ping", ping_command))
        application.add_handler(CommandHandler("check", check_single))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        logger.info("✅ تم إضافة جميع المعالجات")
        logger.info("🤖 البوت جاهز للعمل!")
        
        # بدء البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {str(e)}")
        sys.exit(1)

# ✅ هذا هو الجزء المصحح
if __name__ == '__main__':
    main()async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب - مبسطة للاختبار"""
    user = update.effective_user
    logger.info(f"📱 مستخدم جديد: {user.id} - {user.first_name}")
    
    try:
        # رسالة ترحيب بسيطة
        welcome_text = (
            f"👋 مرحباً {user.first_name}!\n\n"
            f"✅ البوت يعمل بنجاح!\n\n"
            f"📊 معلومات البوت:\n"
            f"• المعرف: {user.id}\n"
            f"• الاسم: {user.first_name}\n"
            f"• الوقت: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔹 استخدم /help لعرض الأوامر المتاحة"
        )
        
        await update.message.reply_text(welcome_text)
        logger.info(f"✅ تم إرسال رسالة الترحيب للمستخدم {user.id}")
        
    except Exception as e:
        logger.error(f"❌ خطأ في دالة start: {str(e)}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    user = update.effective_user
    logger.info(f"📱 أمر help من المستخدم: {user.id}")
    
    help_text = (
        "🆘 **مساعدة البوت**\n\n"
        "**الأوامر المتاحة:**\n"
        "/start - بدء التشغيل\n"
        "/help - عرض هذه المساعدة\n"
        "/ping - اختبار الاتصال\n"
        "/check [بطاقة] - فحص بطاقة واحدة\n"
        "/mass - فحص عدة بطاقات\n\n"
        "**صيغة البطاقة:**\n"
        "رقم|شهر|سنة|cvv\n"
        "مثال: `/check 4111111111111111|12|25|123`\n\n"
        "⚠️ **تحذير**: هذا البوت للأغراض التعليمية فقط"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر اختبار الاتصال"""
    user = update.effective_user
    logger.info(f"📱 أمر ping من المستخدم: {user.id}")
    
    start_time = time.time()
    await update.message.reply_text("🏓 جاري اختبار الاتصال...")
    end_time = time.time()
    
    response_time = (end_time - start_time) * 1000
    await update.message.reply_text(f"🏓 **بونغ!**\n⏱️ وقت الاستجابة: {response_time:.2f} مللي ثانية", parse_mode='Markdown')

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فحص بطاقة واحدة"""
    user = update.effective_user
    logger.info(f"📱 أمر check من المستخدم: {user.id}")
    
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من وجود البطاقة
    if not context.args:
        await update.message.reply_text(
            "❌ يرجى إدخال البطاقة\n"
            "مثال: `/check 4111111111111111|12|25|123`"
        )
        return
    
    card = ' '.join(context.args).strip()
    logger.info(f"💳 فحص بطاقة: {card[:10]}...")
    
    # التحقق من الصيغة
    if not validate_card_format(card):
        await update.message.reply_text(
            "❌ صيغة غير صحيحة\n"
            "الصيغة: رقم|شهر|سنة|cvv\n"
            "مثال: 4111111111111111|12|25|123"
        )
        return
    
    status_msg = await update.message.reply_text("🔄 جاري الفحص...")
    
    try:
        result = m3_iw(card)
        logger.info(f"✅ نتيجة الفحص: {result}")
        
        emoji = "✅" if "Charge !" in result else "❌"
        
        response = (
            f"{emoji} **النتيجة**\n\n"
            f"💳 البطاقة: `{card}`\n"
            f"📊 الحالة: {result}"
        )
        
        await status_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ خطأ في الفحص: {str(e)}")
        await status_msg.edit_text(f"❌ خطأ: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام"""
    logger.error(f"❌ حدث خطأ: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ عذراً، حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."
            )
    except:
        pass

def validate_card_format(card):
    """التحقق من صيغة البطاقة"""
    parts = card.split('|')
    if len(parts) != 4:
        return False
    if not all(parts):
        return False
    if not parts[0].isdigit():
        return False
    return True

def m3_iw(ccx):
    """دالة الفحص الأصلية مع تحسين معالجة الأخطاء"""
    try:
        ccx = ccx.strip()
        parts = ccx.split("|")
        
        if len(parts) != 4:
            return "خطأ: صيغة البطاقة غير صحيحة"
            
        n = parts[0].strip()
        mm = parts[1].strip()
        yy = parts[2].strip()
        cvc = parts[3].strip()

        # التحقق من صحة البيانات
        if not n.isdigit() or len(n) < 15:
            return "خطأ: رقم البطاقة غير صحيح"
            
        if not mm.isdigit() or int(mm) < 1 or int(mm) > 12:
            return "خطأ: الشهر غير صحيح"
            
        # معالجة السنة
        if "20" in yy:
            yy = yy.split("20")[1]
        if not yy.isdigit() or len(yy) != 2:
            return "خطأ: السنة غير صحيحة"
            
        if not cvc.isdigit() or len(cvc) < 3:
            return "خطأ: الرقم السري غير صحيح"
        
        # هنا يمكنك إضافة كود الفحص الفعلي
        # هذا مجرد مثال للاختبار
        time.sleep(1)  # محاكاة وقت الفحص
        
        # للاختبار فقط - يمكنك استبدال هذا بالكود الأصلي الكامل
        # إذا كان الرقم يبدأ بـ 4 (فيزا) نعطي نتيجة ناجحة للاختبار
        if n.startswith('4'):
            return "✅ Charge ! (تمت الموافقة)"
        elif n.startswith('5'):
            return "⚠️ بطاقة ماستركارد - تحتاج فحص إضافي"
        else:
            return "❌ تم الرفض - بطاقة غير مدعومة"
        
    except Exception as e:
        logger.error(f"خطأ في m3_iw: {str(e)}")
        return f"خطأ في الفحص: {str(e)}"

def main():
    """الدالة الرئيسية"""
    logger.info("🚀 بدء تشغيل البوت...")
    
    try:
        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ تم إنشاء تطبيق البوت")
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("ping", ping_command))
        application.add_handler(CommandHandler("check", check_single))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        logger.info("✅ تم إضافة جميع المعالجات")
        logger.info("🤖 البوت جاهز للعمل!")
        
        # بدء البوت
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()ypto

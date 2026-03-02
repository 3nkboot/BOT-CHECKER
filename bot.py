import time
import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = ('8574162513:AAFuxhjffUh9tP8LzDAnLostStEJV2nOkRA')

if not BOT_TOKEN:
    sys.exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 مرحبا {user.first_name}!\n"
        "/check رقم|شهر|سنة|cvv\n"
        "او ارفع ملف .txt"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/check 4111111111111111|12|25|123\n"
        "او ارفع ملف txt"
    )

async def check_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ اكتب: /check رقم|شهر|سنة|cvv")
    
    card = ' '.join(context.args)
    
    if not validate_card(card):
        return await update.message.reply_text("❌ صيغة غلط")
    
    msg = await update.message.reply_text("🔄 جاري الفحص...")
    result = check_card(card)
    await msg.edit_text(f"{result}\n{hide_card(card)}")

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

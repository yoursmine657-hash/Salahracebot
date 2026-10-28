import os
import asyncio
import threading
from datetime import datetime
import pytz
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# --- Keep Render alive ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "Salah Bot Alive - Eldoret"
def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# --- Config ---
TOKEN = os.getenv("TOKEN")
GROUP_ID = -1003710189896
EAT = pytz.timezone("Africa/Nairobi")

TIMES = {
    "Fajr": "05:09",
    "Dhuhr": "12:23",
    "Asr": "13:35",
    "Maghrib": "18:26",
    "Isha": "19:32"
}

sent_today = set()

async def checker(app: Application):
    while True:
        now_str = datetime.now(EAT).strftime("%H:%M")
        today = str(datetime.now(EAT).date())
        for name, t in TIMES.items():
            key = (today, name)
            if now_str == t and key not in sent_today:
                kb = [[InlineKeyboardButton(f"✅ I prayed {name}", callback_data=f"pray:{name}")]]
                try:
                    await app.bot.send_message(
                        GROUP_ID, 
                        f"⏰ *{name}* Salah - {t}\nWho prayed? Tap below 👇",
                        reply_markup=InlineKeyboardMarkup(kb),
                        parse_mode='Markdown'
                    )
                    print(f"Sent {name} at {t}")
                    sent_today.add(key)
                except Exception as e:
                    print(f"FAILED to send {name}: {e}")
        await asyncio.sleep(30)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    name = q.data.split(":")[1]
    time_now = datetime.now(EAT).strftime("%H:%M")
    await q.edit_message_text(f"✅ {q.from_user.first_name} prayed {name} at {time_now}")

async def main():
    if not TOKEN:
        print("ERROR: TOKEN not found in Render Environment!")
        return
    print("Bot starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(on_button))
    
    # Start checker in background
    asyncio.create_task(checker(app))
    
    # Test message to confirm bot is online
    try:
        await app.bot.send_message(GROUP_ID, "✅ Bot restarted and ONLINE - Will post Salah times")
        print("Test ONLINE message sent")
    except Exception as e:
        print(f"Test message failed (check admin/group ID): {e}")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

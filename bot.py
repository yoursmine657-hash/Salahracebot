import os, asyncio
from datetime import datetime
import pytz
from flask import Flask
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# --- Keep Render alive ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Salah Bot Alive"
def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# --- Config ---
TOKEN = os.getenv("TOKEN")
GROUP_ID = -1003710189896  # your group
EAT = pytz.timezone("Africa/Nairobi")

# Real Eldoret times for today - bot will handle it
TIMES = {
    "Fajr": "04:50",
    "Dhuhr": "12:30",
    "Asr": "13:30",
    "Maghrib": "18:15",
    "Isha": "19:30"
}

sent = set()

async def checker(app):
    while True:
        now = datetime.now(EAT).strftime("%H:%M")
        today = str(datetime.now(EAT).date())
        for name, t in TIMES.items():
            key = (today, name)
            if now == t and key not in sent:
                kb = [[InlineKeyboardButton(f"✅ I prayed {name}", callback_data=f"pray:{name}")]]
                try:
                    await app.bot.send_message(GROUP_ID, f"⏰ *{name}* - {t}\nWho prayed? Tap!", reply_markup=InlineKeyboardMarkup(kb), parse_mode='Markdown')
                except Exception as e:
                    print(e)
                sent.add(key)
        await asyncio.sleep(30)

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(f"✅ {q.from_user.first_name} prayed {q.data.split(':')[1]} - {datetime.now(EAT).strftime('%H:%M')}")

async def main():
    print("Bot starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(on_button))
    asyncio.create_task(checker(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

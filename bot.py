import os, asyncio
from datetime import datetime
import pytz
from flask import Flask
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# Keep Render alive
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot alive - Salaat on time"
threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=10000), daemon=True).start()

TOKEN = os.getenv("TOKEN")
GROUP_ID = -1003710189896  # REPLACE WITH YOUR GROUP ID
EAT = pytz.timezone("Africa/Nairobi")

TIMES = {"Fajr":"05:30","Dhuhr":"13:00","Asr":"16:15","Maghrib":"18:45","Isha":"20:00"}
sent_times = set()
leaderboard = {}

async def check_loop(app):
    while True:
        now = datetime.now(EAT).strftime("%H:%M")
        today = datetime.now(EAT).date()
        for name,t in TIMES.items():
            k = (str(today), name)
            if now == t and k not in sent_times:
                kb = [[InlineKeyboardButton(f"✅ I prayed {name}", callback_data=f"claim:{name}")]]
                await app.bot.send_message(GROUP_ID, f"⏰ {name} - {t}\nClick to claim!", reply_markup=InlineKeyboardMarkup(kb))
                sent_times.add(k)
        if now == "00:01": sent_times.clear()
        await asyncio.sleep(30)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if not data.startswith("claim:"): return
    pr = data.split(":")[1]
    user = q.from_user.id
    k = (str(datetime.now(EAT).date()), pr)
    if k in leaderboard.get(user, {}): 
        await q.answer("You already claimed!", show_alert=True)
        return
    leaderboard.setdefault(user, set()).add(k)
    await q.edit_message_text(f"✅ {q.from_user.first_name} prayed {pr} Alhamdulillah!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_click))
    asyncio.create_task(check_loop(app))
    await app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())

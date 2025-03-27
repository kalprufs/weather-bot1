import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from dotenv import load_dotenv
from datetime import time
import pytz

# Load env vars
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWM_KEY = os.getenv("OPENWEATHER_API_KEY")

# Track active users
active_users = set()

# Clothing recommendations
def get_clothing(temp: float) -> str:
    if temp < 0:
        return "❄️ Bundle up! Wear a heavy coat, gloves, and a scarf."
    elif temp < 10:
        return "🧥 Wear a warm jacket and layers."
    elif temp < 20:
        return "🧣 Light jacket or sweater is perfect."
    else:
        return "☀️ T-shirt and shorts weather!"

async def get_tehran_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Tehran&appid={OWM_KEY}&units=metric"
    try:
        data = requests.get(url).json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        clothes = get_clothing(temp)
        return (
            f"🌡️ Tehran: {temp}°C, {desc.capitalize()}\n"
            f"👗 Outfit Tip: {clothes}"
        )
    except:
        return "❌ Couldn't fetch weather data."

async def send_daily_update(context: CallbackContext):
    """Send to all users who started the bot"""
    for chat_id in active_users:
        weather = await get_tehran_weather()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🌙 Good morning! Here's your weather:\n\n{weather}"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Register user and send welcome"""
    chat_id = update.effective_chat.id
    active_users.add(chat_id)  # Add to daily updates list
    
    weather = await get_tehran_weather()
    await update.message.reply_text(
        f"🌤️ Weather Bot Activated!\n\n"
        f"{weather}\n\n"
        f"✅ You'll now get daily updates at 12 AM Tehran time!"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Schedule daily message at 00:00 Tehran time (20:30 UTC)
    job_queue = app.job_queue
    job_queue.run_daily(
        send_daily_update,
        time=time(hour=20, minute=30, tzinfo=pytz.timezone("Asia/Tehran")),
    )
    
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot is running with user-based scheduling!")
    app.run_polling()

if __name__ == "__main__":
    main()
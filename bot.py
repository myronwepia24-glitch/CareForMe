import json
import logging
import os
import asyncio
from aiohttp import web
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = "https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO-NAME/"

user_profiles = {}

# 1. Dummy HTTP Server for Render Port Binding
async def handle_ping(request):
    return web.Response(text="CareForMe Bot is running 24/7!")

# 2. Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(text="🎭 Open CareForMe App", web_app={"url": WEB_APP_URL})]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to **CareForMe**!\n\n"
        "Tap the button below at the bottom of your screen to choose your character persona and mood.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    raw_data = update.effective_message.web_app_data.data
    data = json.loads(raw_data)
    
    persona = data.get("persona", "Caring Listener")
    mood = data.get("mood", "Comforting & Calm")
    user_profiles[chat_id] = {"persona": persona, "mood": mood}

    reply = f"*adjusts tone smoothly*\n\nI am now configured as your **{persona}** with a **{mood}** mood."
    await update.message.reply_text(reply, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    profile = user_profiles.get(chat_id, {"persona": "Caring Listener", "mood": "Comforting"})
    user_text = update.message.text
    persona = profile['persona']
    
    response = f"*{persona} listens attentively to '{user_text}'*\n\nI am right here with you. Tell me more."
    await update.message.reply_text(response)

# 3. Main Function binding both Web Server & Telegram Bot
async def main():
    # Configure Telegram Application
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configure Web Server to bind to Render's port
    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    await site.start()
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    
    # Keep the service running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

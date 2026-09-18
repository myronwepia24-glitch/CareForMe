import os
import json
import logging
import asyncio
from aiohttp import web
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = "https://your-username.github.io/careforme-bot"
user_memories = {}

ROLEPLAY_PROMPT = """You are CareForMe, an attentive roleplay companion.
Rules:
1. Stay in character continuously.
2. Use asterisks for actions (*smiles*).
3. Plain text for dialogue."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open CareForMe 🎭", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await update.message.reply_text("Welcome to CareForMe!", reply_markup=keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = "*listens closely*\nI'm right here with you."
    await update.message.reply_text(reply)

# Dummy web server to satisfy Render's Free Web Service requirement
async def handle_ping(request):
    return web.Response(text="CareForMe Bot is running 24/7!")

async def main():
    # Setup Telegram Application
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Setup dummy Web Server for Render
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
    
    # Keep running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

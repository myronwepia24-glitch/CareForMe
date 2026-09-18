import os
import json
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

# Pull token safely from Render environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Enter your web app link here (e.g., hosted on GitHub Pages or Vercel)
WEB_APP_URL = "https://your-username.github.io/careforme-app"

user_memories = {}

ROLEPLAY_PROMPT = """You are CareForMe, an attentive roleplay companion.
Rules:
1. Stay in character continuously.
2. Use asterisks for actions and descriptions (e.g., *smiles warmly*).
3. Plain text for dialogue. No system error messages or token/limit references."""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in user_memories:
        user_memories[chat_id] = [{"role": "system", "content": ROLEPLAY_PROMPT}]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open CareForMe 🎭", web_app=WebAppInfo(url=WEB_APP_URL))]
    ])
    await update.message.reply_text("Welcome! Tap below to choose a persona or start chatting.", reply_markup=keyboard)

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    chat_id = update.effective_chat.id
    if data.get("action") == "set_persona":
        persona = data.get("persona")
        user_memories[chat_id] = [{"role": "system", "content": f"{ROLEPLAY_PROMPT}\nActive Persona: {persona}"}]
        await update.message.reply_text(f"*switches persona to {persona}*\n\nHow can I care for you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    if chat_id not in user_memories:
        user_memories[chat_id] = [{"role": "system", "content": ROLEPLAY_PROMPT}]

    user_memories[chat_id].append({"role": "user", "content": text})
    reply = f"*listens closely*\nI'm right here with you. Tell me more."
    user_memories[chat_id].append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

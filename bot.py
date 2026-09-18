import json
import logging
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# Make sure to replace this URL with your actual GitHub Pages link!
WEB_APP_URL = "https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO-NAME/"

# In-memory storage for user persona settings
user_profiles = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # KeyboardButton with web_app is required for tg.sendData() to work
    keyboard = [[KeyboardButton(text="🎭 Open CareForMe App", web_app={"url": WEB_APP_URL})]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Welcome to **CareForMe**!\n\n"
        "Tap the button below at the bottom of your screen to choose your character persona and mood.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in user_profiles:
        del user_profiles[chat_id]
    await update.message.reply_text("*resets conversation context and memory back to clean state*")

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    raw_data = update.effective_message.web_app_data.data
    data = json.loads(raw_data)
    
    persona = data.get("persona", "Caring Listener")
    mood = data.get("mood", "Comforting & Calm")
    
    # Store settings for user session
    user_profiles[chat_id] = {"persona": persona, "mood": mood}

    reply = (
        f"*adjusts tone smoothly*\n\n"
        f"I am now configured as your **{persona}** with a **{mood}** mood.\n"
        f"How are you feeling right now?"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    profile = user_profiles.get(chat_id, {"persona": "Caring Listener", "mood": "Comforting"})
    
    user_text = update.message.text
    persona = profile['persona']
    
    # Context-aware roleplay response template
    response = f"*{persona} listens attentively to '{user_text}'*\n\nI am right here with you. Let me know what else is on your mind."
    await update.message.reply_text(response)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()

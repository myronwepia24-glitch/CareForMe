import json, logging, os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = "https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO-NAME/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Keyboard button is required for tg.sendData() to send messages back
    keyboard = [[KeyboardButton(text="🎭 Open CareForMe", web_app=WebAppInfo(url=WEB_APP_URL))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Welcome to CareForMe! Tap the button below to choose your AI persona:",
        reply_markup=reply_markup
    )

# Handle selection from the Mini App
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    persona = data.get("persona", "Companion")
    
    await update.message.reply_text(
        f"*smiles softly*\n\nI am now configured as your **{persona}**. How can I care for you today?"
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.run_polling()

if __name__ == "__main__":
    main()

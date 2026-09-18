import json
import os
import asyncio
import requests
from aiohttp import web
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPO-NAME/")

user_profiles = {}
chat_memories = {}

async def handle_ping(request):
    return web.Response(text="Server Active")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(text="🎭 Open Character Roster", web_app={"url": WEB_APP_URL})]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Select a character or configure a persona:", reply_markup=reply_markup)

async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = json.loads(update.effective_message.web_app_data.data)
    
    user_profiles[chat_id] = {
        "persona": data.get("persona", "Companion"),
        "prompt": data.get("system_prompt", "You are an engaging roleplay partner.")
    }
    chat_memories[chat_id] = []
    await update.message.reply_text(f"Active character set to **{data.get('persona')}**.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    profile = user_profiles.get(chat_id, {"persona": "Companion", "prompt": "You are a roleplay partner."})
    if chat_id not in chat_memories:
        chat_memories[chat_id] = []
        
    chat_memories[chat_id].append({"role": "user", "content": user_text})
    
    system_instruction = f"{profile['prompt']} Roleplay as '{profile['persona']}'. Use asterisks for actions."
    messages = [{"role": "system", "content": system_instruction}] + chat_memories[chat_id][-10:]
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gryphe/mythomax-l2-13b",
        "messages": messages,
        "temperature": 0.85,
        "max_tokens": 350
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        bot_reply = response.json()["choices"][0]["message"]["content"]
        chat_memories[chat_id].append({"role": "assistant", "content": bot_reply})
        await update.message.reply_text(bot_reply)
    except Exception:
        await update.message.reply_text("*glitches* Connection error to model host.")

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    server = web.Application()
    server.router.add_get("/", handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 10000)))
    await site.start()
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

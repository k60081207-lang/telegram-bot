import os
import asyncio
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# ==============================
# Ключі тепер підтягуються автоматично з налаштувань Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==============================

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Пам'ять розмови для кожного користувача
user_chats = {}

SYSTEM_PROMPT = """Ти — розумний особистий AI-помічник. Ти допомагаєш:
- Відповідати на будь-які питання
- Писати тексти, пости, листи, описи
- Планувати задачі та давати поради для бізнесу
- Консультувати по різних темах

Відповідай українською мовою. Будь дружнім, чітким і корисним.
Якщо задача складна — розбий відповідь на кроки."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats[user_id] = []  # скидаємо розмову
    await update.message.reply_text(
        "👋 Привіт! Я твій AI-помічник.\n\n"
        "Я можу:\n"
        "✅ Відповідати на питання\n"
        "✅ Писати тексти, пости, листи\n"
        "✅ Допомагати з бізнес-задачами\n\n"
        "Просто напиши мені що потрібно! 🚀\n\n"
        "Команди:\n"
        "/start — почати заново\n"
        "/clear — очистити розмову"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_chats[user_id] = []
    await update.message.reply_text("🧹 Розмову очищено! Починаємо з чистого аркуша.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    # Ініціалізація якщо новий користувач
    if user_id not in user_chats:
        user_chats[user_id] = []

    # Показуємо що бот думає
    thinking_msg = await update.message.reply_text("⏳ Думаю...")

    try:
        # Будуємо повідомлення з контекстом
        messages = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        
        # Додаємо історію розмови
        for msg in user_chats[user_id][-10:]:  # останні 10 повідомлень
            messages.append(msg)
        
        # Додаємо нове питання
        messages.append({"role": "user", "parts": [user_text]})

        # Запит до Gemini
        response = model.generate_content(messages)
        bot_reply = response.text

        # Зберігаємо в пам'яті
        user_chats[user_id].append({"role": "user", "parts": [user_text]})
        user_chats[user_id].append({"role": "model", "parts": [bot_reply]})

        # Видаляємо "Думаю..." і надсилаємо відповідь
        await thinking_msg.delete()
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await thinking_msg.edit_text(f"❌ Помилка: {str(e)}\n\nСпробуй ще раз!")


def main():
    # Використовуємо правильний метод підключення
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Додаємо ваші команди та обробник повідомлень
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот успішно запущений...")
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
